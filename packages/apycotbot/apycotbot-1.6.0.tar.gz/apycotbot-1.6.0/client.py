"""APyCoT client sending commands to the bot

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import sys
from time import localtime, mktime

from logilab.common import pyro_ext as pyro
from logilab.common.clcommands import Command, main_run, register_commands
from logilab.common.tasksqueue import REVERSE_PRIORITY

from apycotbot import ConfigError, NotSupported
from apycotbot.utils import (PYRO_NS_OPTIONS, PYRO_OPTIONS, CW_OPTIONS,
                             TEST_OPTIONS, RESOURCES_OPTIONS, ConnectionHandler)
from apycotbot.writer import DataWriter
from apycotbot.repositories import get_repository


def format_task_dict(tdict):
    tdict['priority'] = REVERSE_PRIORITY[tdict['priority']]
    return '%(envname)s %(tcname)s(%(eid)s) with priority %(priority)s on branch %(branch)s' % tdict


class ApycotCommand(Command):
    """base class for apycot commands"""
    options = PYRO_OPTIONS

    def proxy(self):
        print 'retrieving proxy to the apycot bot...',
        sys.stdout.flush()
        proxy = pyro.ns_get_proxy(self['pyro-id'], defaultnsgroup='apycot',
                                  nshost=self['pyro-ns-host'])
        print 'done.'
        return proxy


CLIENT_TEST_OPTIONS = (
    ('branch',
     {'type' : 'string', 'short': 't',
      'help': 'forced a vcs revision branch for main project',
      'default': None,
      'group': 'main', 'inputlevel': 2,
      }),
    ('keep-test-dir',
     {'action' : 'store_true',
      'help': 'keep temporary directory where the test environment has been built',
      'group': 'main', 'inputlevel': 2,
      }),
    ('archive',
     {'action' : 'store_true',
      'help': 'store the content of temporary directory where the test environment has been built in an archive',
      'group': 'main', 'inputlevel': 2,
      }),
)

class StartTaskCommand(ApycotCommand):
    """add a task to the bot queue."""
    name = 'start'
    arguments = '<project environment> <test config name>'
    min_args = 0
    options = (
        ('priority',
         {'type' : 'choice', 'short': 'p',
          'choices': ('LOW', 'MEDIUM', 'HIGH'),
          'default': 'MEDIUM',
          'help': 'priority of the task to launch',
          'group': 'main', 'inputlevel': 2,
          }),
        ('start-reverse-dependencies',
         {'action':  'store_true', 'short': 's',
          'help': 'Start tests for projects depending from listed projects.',
          'group': 'main', 'inputlevel': 2,
          }),
        ) + CLIENT_TEST_OPTIONS + ApycotCommand.options

    def start_tasks(self, tests, branch, start_deps, keep_test_dir=False,
                    archive=False, priority="MEDIUM"):
        proxy = self.proxy()
        if not tests:
            proxy.queue_all(branch=branch,
                            start_deps=start_deps,
                            keep_test_dir=keep_test_dir,
                            archive=archive,
                            priority=priority)
        else:
            envname, tcname = tests
            try:
                proxy.queue_task(envname, tcname,
                                 branch=branch,
                                 start_rev_deps=start_deps,
                                 keep_test_dir=keep_test_dir,
                                 archive=archive,
                                 priority=priority)
            except Exception, ex:
                print >>sys.stderr, 'error while queuing task %s %s: %s' % (
                    envname, tcname, ex)


    def run(self, tests):
        self.start_tasks(tests, self['branch'],
                         self['start-reverse-dependencies'],
                         self['keep-test-dir'],
                         self['archive'],
                         self['priority'])


class CancelTaskCommand(ApycotCommand):
    """cancel a task or a list of tasks."""
    name = 'cancel'
    arguments = '<task id>...'
    def run(self, tasks):
        proxy = self.proxy()
        for tid in tasks:
            proxy.cancel_task(tid)


class ListTasksCommand(ApycotCommand):
    """list pending tasks."""
    name = 'list'
    def run(self, args):
        pending, running = self.proxy().pending_tasks()
        if pending:
            print 'pending tasks'
            for tdict in pending:
                print '*', format_task_dict(tdict)
            print
        else:
            print 'no pending task'
        if running:
            print 'running tasks'
            for tdict in running:
                print '*', format_task_dict(tdict)
            print
        else:
            print 'no running task'


class ListChangesCommand(ApycotCommand):
    """report changes in repositories according to apycot configuration found.

    This command access directly to the cubicweb instance to get necessary
    information, no access to the apycot bot.

    Exit with 0 status if some activity has been detected, else 1.
    """
    name = 'changes'
    arguments = '[<project apycot config name>...]'
    options = CW_OPTIONS + (
        ('minutes-offset',
         {'type' : 'int', 'short': 'M',
          'default': 60,
          'help': 'offset in minutes since which changes should be considered',
          'group': 'main', 'inputlevel': 2,
          }),
        ('verbose',
         {'action' : 'store_true', 'short': 'v',
          'help': "If not given, only print names of project's configuration \
where some activity has been detected (one per line), else changes are \
actually printed on stdout",
          'group': 'main', 'inputlevel': 2,
          }),
        ) + PYRO_NS_OPTIONS

    def run(self, tests):
        offset = self['minutes-offset'] * 60 # in seconds
        if not offset:
            raise ConfigError('you must have a non-zero offset')
        encoding = sys.stdout.encoding
        to_date = localtime()
        from_date = localtime(mktime(to_date) - offset)
        status = 1
        cnxhdlr = ConnectionHandler(self['cw-inst-id'], self['pyro-ns-host'])
        cnx = cnxhdlr.connect()
        if cnx is None:
            raise ConfigError('can\'t connect to cubicweb instance')
        cu = cnx.cursor()
        try:
            if tests:
                rql = ('Any X,N WHERE X is TestConfig, X name N, X name IN (%s)' %
                       ','.join('"%s"' % test for test in tests))
            else:
                rql = 'Any X,N WHERE X is TestConfig, X name N, X in_state S, S name "activated"'
            for pac in cu.execute(rql).entities():
                repo = apyrep = get_repository(pac.apycot_repository_def)
                try:
                    logs = list(repo.log_info(from_date, to_date))
                except NotSupported:
                    continue
                if not logs:
                    continue
                status = 0
                print pac.name
                if self['verbose']:
                    print '*'*len(pac.name)
                    for chkininfo in logs:
                        msg = chkininfo.message_summary().encode(encoding)
                        print '%s: %s' % (chkininfo.author, msg)
                    print
            if self['verbose'] and status:
                print 'no changes'
            sys.exit(status)
        finally:
            cnxhdlr.close()


class RunTestCommand(ApycotCommand):
    """run tests for a given apycot configuration.

    This command access directly to the cubicweb instance to get necessary
    information, no access to the apycot bot.
    """
    name = 'run'
    arguments = '<project environment> <test config name>'
    min_args = 2
    max_args = 2
    options = CW_OPTIONS + CLIENT_TEST_OPTIONS + TEST_OPTIONS \
              + RESOURCES_OPTIONS + PYRO_NS_OPTIONS

    def run(self, tests):
        if not tests:
            raise ConfigError('please specify an environment and a configuration to test')
        if len(tests) != 2:
            raise ConfigError('only one configuration is supported')
        from apycotbot.task import Test
        # trigger registering
        from apycotbot import preprocessors
        from apycotbot import checkers
        envname, tcname = tests
        cnxhdlr = ConnectionHandler(self['cw-inst-id'], self['pyro-ns-host'])
        try:
            tconfig = cnxhdlr.test_config(envname, tcname, reconnect=False)
            writer = DataWriter(cnxhdlr, tconfig.eid)
            # load plugins if necessary
            if self['plugins']:
                for module in self['plugins']:
                    writer.info('loading extra module %s', module)
                    try:
                        __import__(module)
                    except Exception:
                        writer.error('while loading %s', module, tb=True)
                        continue
            # instantiate a Test
            test = Test(cnxhdlr.cnx, tconfig, writer, dict(self))
            test.execute()
            sys.exit(0)
        finally:
            cnxhdlr.close()

register_commands((StartTaskCommand,
                   ListTasksCommand,
                   CancelTaskCommand,
                   ListChangesCommand,
                   RunTestCommand,
                   ))


def run():
    """command line tool"""
    main_run(sys.argv[1:], """%%prog %s [options] %s

Apycot bot client.
%s""")
