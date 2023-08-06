"""APyCoT bot waiting for pyro connection

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import os
import sys
import select
import warnings
import signal
import stat
import logging
from os.path import exists, join, normpath
from subprocess import Popen
from tempfile import TemporaryFile
from threading import Thread, Lock, Timer

from datetime import datetime, timedelta

from Pyro import config
# disable multithread support so we can share a connection to the cw
# instlication. Since each commands should be very quickly acheived, this should
# not be a penalty
config.PYRO_MULTITHREADED = False
config.PYRO_STDLOGGING = True
config.PYRO_TRACELEVEL = 3
config.PYRO_TRACEBACK_USER_LEVEL = 3
config.PYRO_DETAILED_TRACEBACK = 1
config.PYRO_STORAGE = '/tmp' # XXX

from logilab.common.logging_ext import set_log_methods, init_log
from logilab.common.configuration import Configuration, Method
from logilab.common import tasksqueue, pyro_ext as pyro

from apycotbot import MODE, ConfigError, list_registered, get_registered
from apycotbot.utils import (PYRO_OPTIONS, CW_OPTIONS, TEST_OPTIONS,
                             RESOURCES_OPTIONS, ConnectionHandler)
from apycotbot.task import ApycotTask, ARCHIVE_EXT, make_archive_name

from apycotbot import checkers, preprocessors # trigger registration


class ApycotBotServer(Configuration):
    options = CW_OPTIONS + (
        ('debug',
         {'action' : 'store_true', 'short': 'D',
          'help': 'start in debug mode',
          'group': 'main', 'inputlevel': 2,
          }),
        ('force',
         {'action' : 'store_true', 'short': 'f',
          'help': 'force server start even if already registered in the pyro \
name server',
          'group': 'main', 'inputlevel': 2,
          }),
        ('generate-rcfile',
         {'action' : 'callback', 'callback' : Method('_generate_config'),
          'group': 'Commands',
          'help' : '''Generate a sample configuration file according to \
the current configuration. You can put other options before this one to get \
them in the generated configuration.'''}),

        ) + TEST_OPTIONS + (

        ('threads',
         {'type' : 'int', 'short': 'T',
          'default': 2,
          'help': 'number of tasks which may be run in parallel',
          'group': 'process-control', 'inputlevel': 2,
          }),

        ) + RESOURCES_OPTIONS + (

        ('uid',
         {'type' : 'string',
          'default': None,
          'help': 'if this option is set, use the specified user to start \
the daemon rather than the user running the command',
          'group': 'pyro-server', 'inputlevel': 1,
          }),
        ('log-file',
         {'type' : 'string',
          'default': Method('_log_file'),
          'help': 'file where output logs should be written',
          'group': 'pyro-server', 'inputlevel': 2,
          }),
       ('log-threshold',
         {'type' : 'string', # XXX use a dedicated type?
          'default': 'INFO',
          'help': 'server\'s log level',
          'group': 'pyro-server', 'inputlevel': 1,
          }),
        ('host',
         {'type' : 'string',
          'default': None,
          'help': 'host name if not correctly detectable through gethostname. '\
          'You can also specify a port using <host>:<port> notation (will be '\
          'choosen randomly if not set (recommended)).',
          'group': 'pyro-server', 'inputlevel': 1,
          }),
        ('pid-file',
         {'type' : 'string',
          'default': Method('_pid_file'),
          'help': 'daemon\'s pid file',
          'group': 'pyro-server', 'inputlevel': 2,
          }),
         ) + PYRO_OPTIONS

    def __init__(self):
        """make the repository available as a PyRO object"""
        Configuration.__init__(self)
        self.load_file_configuration(self._configuration_file)
        args = self.load_command_line_configuration()
        if args:
            print self.help()
            raise ConfigError('too many arguments')
        self._queue = tasksqueue.PrioritizedTasksQueue()
        self._quiting = None
        self._running_tasks = set()
        self._lock = Lock()
        # interval of time where task queued while there is an identical task
        # running will be ignored
        self._skip_duplicate_time_delta = timedelta(seconds=15)
        # load plugins if necessary, to get info about them in available_*
        # methods
        if self['plugins']:
            for module in self['plugins']:
                writer.info('loading extra module %s', module)
                try:
                    __import__(module)
                except Exception:
                        writer.error('while loading %s', module, tb=True)
                        continue

    if MODE == 'dev':
        _default_conf_file = os.path.expanduser('~/etc/apycotbot.ini')
        _default_pid_file = '/tmp/apycotbot.pid'
        _default_log_file = '/tmp/apycotbot.log'
    else:
        _default_conf_file = '/etc/apycotbot.ini'
        _default_pid_file = '/var/run/apycotbot/apycotbot.pid'
        _default_log_file = '/var/log/apycotbot/apycotbot.log'

    @property
    def _configuration_file(self):
        return os.environ.get('APYCOTBOTRC', self._default_conf_file)

    def _pid_file(self):
        return self._default_pid_file

    def _log_file(self):
        return self._default_log_file

    def start(self):
        if self['debug']:
            logthreshold = 'DEBUG'
        else:
            logthreshold = self['log-threshold']
        init_log(self['debug'], logthreshold=logthreshold,
                 logfile=self['log-file'])
        pyro.set_pyro_log_threshold(getattr(logging, self['log-threshold']))
        if self['force']:
            pyro.ns_unregister(self['pyro-id'], defaultnsgroup='apycot',
                               nshost=self['pyro-ns-host'])
        self._install_sig_handlers()
        self._daemon = pyro.register_object(self, self['pyro-id'],
                                            defaultnsgroup='apycot',
                                            daemonhost=self['host'],
                                            nshost=self['pyro-ns-host'])
        # go ! (don't daemonize in debug mode)
        if not self['debug'] and self._daemonize(self['pid-file']) == -1:
            return
        # change process uid
        if self['uid']:
            try:
                uid = int(self['uid'])
            except ValueError:
                from pwd import getpwnam
                uid = getpwnam(self['uid']).pw_uid
            os.setuid(uid)
        self._loop()

    def _loop(self, req_timeout=0.5):
        """enter the service loop"""
        try:
            while self._quiting is None:
                try:
                    self._daemon.handleRequests(req_timeout)
                except select.error:
                    continue
                try:
                    self._start_tasks()
                except SystemExit:
                    raise
                except Exception, ex:
                    self.exception('error while starting task: %s', ex)
        finally:
            pyro.ns_unregister(self['pyro-id'], defaultnsgroup='apycot',
                               nshost=self['pyro-ns-host'])
            self.info('exit')

    def _quit(self):
        """stop the server"""
        self._quiting = True

    def _generate_config(self, *args, **kwargs):
        """optik callback for sample config file generation"""
        self.generate_config(skipsections=('COMMANDS',))
        sys.exit(0)

    # server utilitities ######################################################

    def _install_sig_handlers(self):
        """install signal handlers"""
        self.info('installing signal handlers')
        signal.signal(signal.SIGINT, lambda x, y, s=self: s._quit())
        signal.signal(signal.SIGTERM, lambda x, y, s=self: s._quit())

    def _daemonize(self, pid_file=None):
        """daemonize the process"""
        # fork so the parent can exist
        if (os.fork()):
            return -1
        # deconnect from tty and create a new session
        os.setsid()
        # fork again so the parent, (the session group leader), can exit.
        # as a non-session group leader, we can never regain a controlling
        # terminal.
        if (os.fork()):
            return -1
        # move to the root to avoit mount pb
        os.chdir('/')
        # set paranoid umask
        os.umask(077)
        if pid_file is not None:
            # write pid in a file
            f = open(pid_file, 'w')
            f.write(str(os.getpid()))
            f.close()
        # filter warnings
        warnings.filterwarnings('ignore')
        # close standard descriptors
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()

    # public (pyro) interface #################################################

    def queue_all(self, branch=None, start_rev_deps=False, keep_test_dir=False,
                  archive=False, priority='LOW', cwid=None):
        """add task to the queue for every activated test config"""
        cnxh = ConnectionHandler(cwid or self['cw-inst-id'],
                                 self['pyro-ns-host'])
        cnxh.connect()
        try:
            for tconfig in cnxh.activated_tests().entities():
                self._queue_tconfig(tconfig, priority, branch, start_rev_deps,
                                    keep_test_dir, archive, cwid)
        finally:
            cnxh.close()

    def queue_task(self, envname, tcname, branch=None, start_rev_deps=False,
                   keep_test_dir=False, archive=False, priority='LOW',
                   cwid=None):
        """add a task to the queue for test config of the given name"""
        cnxh = ConnectionHandler(cwid or self['cw-inst-id'],
                                 self['pyro-ns-host'])
        cnxh.connect()
        try:
            tconfig = cnxh.test_config(envname, tcname)
            self._queue_tconfig(tconfig, priority, branch, start_rev_deps,
                                keep_test_dir, archive, cwid)
        finally:
            cnxh.close()

    def _queue_tconfig(self, tconfig, priority, branch, start_rev_deps,
                       keep_test_dir, archive,  cwid):
        msg = 'queuing test %s (%s) with priority %s'
        args = (tconfig.name, tconfig.environment.name, priority)
        if not tconfig.all_checks:
            self.warning('no check defined for %s. Exit.' % tconfig.name)
            return
        if self._already_running(tconfig, branch):
            self.info('don\'t queue already running test %s for branch %s',
                      tconfig.name, branch)
            return
        if branch:
            msg = msg + ' for branch %s'
            args += (branch,)
        self.info(msg, *args)
        from_inst_id = tconfig.metainformation()['source']['uri']
        if from_inst_id == 'system':
            from_inst_id = cwid or self['cw-inst-id']
        self._queue.put(ApycotTask(tconfig.eid,
                                   tconfig.environment.name, tconfig.name, from_inst_id,
                                   getattr(tasksqueue, priority),
                                   branch=branch,
                                   keep_test_dir=keep_test_dir,
                                   archive=archive,
                                   archive_dir=self["archive-dir"]))
        if start_rev_deps:
            self.info('starting reverse dependencies')
            for pe in tconfig.environment.reverse_needs_checkout:
                # pe may be a test config
                for tc in getattr(pe, 'reverse_use_environment', ()):
                    if tc.state == 'activated' and tc.name == tconfig.name:
                        self._queue_tconfig(tc, priority, branch,
                                            start_rev_deps=False,
                                            keep_test_dir=keep_test_dir,
                                            archive=archive,
                                            cwid=cwid)
                    else:
                        self.info('skipped configuration %s (%s) for branch %s',
                                  tc.name, tc.state, branch)

    def pending_tasks(self):
        """return an ordered list of task pending in the queue, from the lowest
        to the highest priority, and another list of currently running task
        """
        return ([t.as_dict() for t in self._queue],
                [t.as_dict() for t in self._running_tasks])

    def cancel_task(self, tid):
        """return an ordered list of task pending in the queue, from the highest
        to the lowest priority
        """
        self._queue.remove(tid)
        self.info('test %s cancelled', tid)

    def available_checkers(self):
        """return a list of dictionaries describing available checkers

        available keys are:
        * `id`, the checker's identifier
        * `help`, the checker's docstring
        * `preprocessor`, required preprocessor or None
        """
        res = []
        for id in sorted(list_registered('checker')):
            checker = get_registered('checker', id)
            res.append({'id': id,
                        'help': checker.__doc__.splitlines()[0].strip(),
                        'preprocessor': checker.need_preprocessor,
                        })
        return res

    def available_preprocessors(self):
        """return a list of dictionaries describing available preprocessors

        available keys are:
        * `id`, the preprocessor's identifier
        * `help`, the preprocessor's docstring
        """
        res = []
        for id in sorted(list_registered('preprocessor')):
            preprocessor = get_registered('preprocessor', id)
            res.append({'id': id,
                        'help': preprocessor.__doc__.splitlines()[0].strip(),
                        })
        return res

    def available_options(self):
        """return a list of dictionaries describing available configuration
        options

        available keys are:
        * `name`, the option's name
        * `id`, the option's id (eg its checker/preprocessor id preprended to
          its name)
        * `help`, the option's description
        * `type`, the option's type
        * `required`, flag telling if the option is required

        optional keys are:
        * `checker`, checker to which this option belongs to
        * `preprocessor`, preprocessor to which this option belongs to
        """
        res = []
        for optname, optdict in TEST_OPTIONS + RESOURCES_OPTIONS:
            res.append({'name': optname,
                        'type': optdict['type'],
                        'help': optdict['help'],
                        })
        for category in ('checker', 'preprocessor'):
            for id in sorted(list_registered(category)):
                obj = get_registered(category, id)
                for optdict in obj.options_def:
                    res.append({'name': optdict['name'],
                                'id': '%s_%s' % (id, optdict['name']),
                                'type': optdict.get('type', 'string'),
                                'required': optdict.get('required', False),
                                'help': optdict['help'],
                                category: id,
                                })
        return res

    def get_archive(self, instance_id, exec_id):
        """get the content of the requested archive.

        Return a String if the archive exist and readable, None otherwise.
        """
        exec_dir = normpath(self["archive-dir"])
        archive_path = join(exec_dir, make_archive_name(instance_id, exec_id))
        try:
            return open(archive_path, mode='rb').read()
        except IOError:
            return None

    def clear_archive(self, instance_id, exec_id):
        """Remove an archive from pyro storage.

        return nale of actually deleted archive"""
        exec_dir = normpath(self["archive-dir"])
        archive_name = make_archive_name(instance_id, exec_id)
        archive_path = join(exec_dir, archive_name)
        if exists(archive_path):
            os.unlink(archive_path)
            return archive_name



    # internal tasks managements ##############################################

    def _start_tasks(self):
        """start pending tasks according to available resources"""
        while self._queue.qsize() and len(self._running_tasks) < self['threads']:
            self._start_task(self._queue.get())

    def _start_task(self, task):
        """start given task in a separated thread"""
        self.info('start test %s', task.id)
        # start a thread to wait for the end of the child process
        task.starttime = datetime.now()
        self._running_tasks.add(task)
        # NOTE: give self instead of self.config to allow subscription
        #       notation
        t = Thread(target=self._run_task, args=(task,))
        t.start()

    def _run_task(self, task):
        """run the task and remove it from running tasks set once finished"""
        try:
            self._run_command(task.run_command(self), task.id)
        finally:
            self._running_tasks.remove(task)
            self.info('test %s finished', task.id)

    def _run_command(self, command, pacname):
        """actually run the task by spawning a subprocess"""
        outfile = TemporaryFile(mode='w+', bufsize=0)
        errfile = TemporaryFile(mode='w+', bufsize=0)
        self.info(' '.join(command))
        cmd = Popen(command, bufsize=0, stdout=outfile, stderr=errfile)
        if self['max-time']:
            max_time = (self['max-time'] + (self['max-reprieve'] or 60) * 1.25)
            timer = Timer(max_time, os.killpg, [cmd.pid, signal.SIGKILL])
            timer.start()
        else:
            timer = None
        cmd.communicate()
        if timer is not None:
            timer.cancel()
        try:
            # kill possible remaining children
            os.killpg(cmd.pid, signal.SIGKILL)
        except OSError, ex:
            if ex.errno != 3:
                raise
        for stream in (outfile, errfile):
            stream.seek(0)
        if cmd.returncode:
            self.error('error while running %s', pacname)
            self.error('`%s` returned with status : %s',
                       ' '.join(command), cmd.returncode)
        if os.fstat(errfile.fileno())[stat.ST_SIZE]:
            self.info('*************** %s error output:', pacname)
            self.info(errfile.read())
        if os.fstat(outfile.fileno())[stat.ST_SIZE]:
            self.info('*************** %s std output:', pacname)
            self.info(outfile.read())

    def _already_running(self, tc, branch):
        """before queuing a task, look at currently running tasks to avoid
        launching the same task twice in a short interval of time
        """
        for task in self._running_tasks:
            if task.id == tc.eid and task.branch == branch and \
                   datetime.now() - task.starttime < self._skip_duplicate_time_delta:
                return True
        return False


LOGGER = logging.getLogger('apycot.bot')
set_log_methods(ApycotBotServer, LOGGER)

def run():
    # create the server
    try:
        server = ApycotBotServer()
    except ConfigError, ex:
        print
        print 'error:', ex
        print
        sys.exit(1)
    server.start()
