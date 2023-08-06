"""APyCoT task / test

A task is a queue (pending) test

A test defines :
* a unit of sources to test (a project)
* a list of checks to apply to this unit
* how to build the test environment (preprocessing, dependencies...)

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import os
import os.path
import tempfile
from shutil import rmtree


import tarfile
from logilab.common.proc import (RESOURCE_LIMIT_EXCEPTION,
                                 ResourceError, ResourceController)
from logilab.common.tasksqueue import LOW, Task
from logilab.common.configuration import format_option_value

from apycotbot import SetupException, ConfigError, get_registered
from apycotbot.utils import (SKIPPED, FAILURE, ERROR, KILLED,
                             EnvironmentTrackerMixin, Command)
from apycotbot.checkers import MissingChecker
from apycotbot.repositories import get_repository

ARCHIVE_EXT = '.tar.bz2'
ARCHIVE_MODE = 'w:bz2'
ARCHIVE_NAME = "apycot-archive-%(instance-id)s-%(exec-id)s"+ARCHIVE_EXT

def make_archive_name(instance_id, execution_id):
    exec_data = {'exec-id': execution_id,
                 'instance-id': instance_id,
                }
    return ARCHIVE_NAME % exec_data


def extract_test_config(config):
    """extract test configuration as a command line options"""
    res = []
    for optname, optdict in config.options:
        if not config.get(optname): # callback actions not in config
            continue
        if optname == 'threads':
            continue
        if optdict.get('group') in ('process-control', 'pyro-name-server') \
           or optname == 'test-dir':
            value = format_option_value(optdict, config[optname])
            res.append('--%s=%s' % (optname, value))
        elif optname == 'plugins':
            res.append('--plugins=%s' % ','.join(optname))
    return res

def substitute(value, substitutions):
    if hasattr(value, 'replace') and value:
        for key, val in substitutions.iteritems():
            value = value.replace('${%s}' % key, val)
    return value

def substitute_dict(dict, substitutions):
    for key, value in dict.iteritems():
        dict[key] = substitute(value, substitutions)
    return dict

def options_from_dict(options, prefix=None):
    """get a dictionary of options begining with <prefix>_ from the given
    dictionary

    <prefix>_ is removed from option's name in the returned dictionary and
    matching keys are removed from the original dictionany
    """
    new_options = {}
    for option, value in options.items():
        if prefix and not option.startswith(prefix + '_'):
            continue
        if prefix:
            new_options[option[len(prefix)+1:]] = value
        else:
            new_options[option] = value
    return new_options


class ApycotTask(Task):

    def __init__(self, tid, envname, tcname, from_inst_id='system', priority=LOW,
                 branch=None, keep_test_dir=False, archive=False,
                 archive_dir=None):
        super(ApycotTask, self).__init__(tid, priority)
        self.tcname = tcname
        self.envname = envname
        self.from_inst_id = from_inst_id
        self.branch = branch
        self.keep_test_dir = keep_test_dir
        self.archive = archive
        self.archive_dir = archive_dir


    def __eq__(self, other):
        return self.id == other.id and self.branch == other.branch

    def as_dict(self):
        return {'eid': self.id,
                'priority': self.priority,
                'tcname': self.tcname,
                'envname': self.envname,
                'instanceid': self.from_inst_id,
                'branch': self.branch,
                'keep_test_dir': self.keep_test_dir
                }

    def run_command(self, mainconfig):
        command = ['apycotclient', 'run', '--cw-inst-id=%s' % self.from_inst_id]
        if self.branch:
            command.append('--branch=%s' % self.branch)
        if self.keep_test_dir:
            command.append('--keep-test-dir')
        if self.archive:
            command.append('--archive')
            if self.archive_dir is not None:
                command.append('--archive-dir=%s' % self.archive_dir)

        command += extract_test_config(mainconfig)
        command.append(self.envname)
        command.append(self.tcname)
        return command


class Test(EnvironmentTrackerMixin):
    """the single source unit test class"""

    def __init__(self, cnx, tconfig, writer, options):
        EnvironmentTrackerMixin.__init__(self)
        # directory where the test environment will be built
        self.tmpdir = tempfile.mkdtemp(dir=options.get('test_dir'))
        # IWriter object
        self.writer = writer
        #
        self.tconfig = tconfig
        self._exec_options = options
        self._cnx = cnx
        self._configs = {}
        self._repositories = {}
        self._preprocessors = {}
        # list of checker objects
        self.checkers = []
        mainconfig = self.apycot_config()
        for name in tconfig.all_checks:
            try:
                chkoptions = options_from_dict(mainconfig, name)
                checker = get_registered('checker', name)(writer, chkoptions)
            except ConfigError, ex:
                checker = MissingChecker(writer, name, str(ex))
            self.checkers.append(checker)
        self.need_preprocessors = set(chk.need_preprocessor for chk in self.checkers
                                      if chk.need_preprocessor is not None)
        # environment variables as a dictionary
        self.environ = substitute_dict(tconfig.apycot_process_environment,
                                       {'NAME': tconfig.name,
                                        'TESTDIR': self.tmpdir})
        # flag indicating whether to clean test environment after test execution
        self.keep_test_dir = options.get('keep_test_dir', False)
        self.archive = options.get('archive', False)
        self.archive_dir = options.get('archive_dir',
                                       options.get('test_dir','/tmp/'))
        os.environ['APYCOT_ROOT'] = self.tmpdir
        # set of preprocessors which have failed
        self._failed_pp = set()
        self.executed_checkers = {}
        # resource controller
        self.resource_ctrl = ResourceController(mainconfig.get('max-cpu-time'),
                                                mainconfig.get('max-time'),
                                                mainconfig.get('max-memory'),
                                                mainconfig.get('max-reprieve'))

    def __str__(self):
        return repr(self.apycot_repository())

    def apycot_config(self, pe_or_tc=None):
        if pe_or_tc is None:
            pe_or_tc = self.tconfig
        try:
            return self._configs[pe_or_tc.eid]
        except KeyError:
            config = pe_or_tc.apycot_configuration
            config.update(self._exec_options)
            substitute_dict(config, {'NAME': pe_or_tc.name, 'TESTDIR': self.tmpdir})
            self._configs[pe_or_tc.eid] = config
            return config

    def apycot_repository(self, pe=None):
        if pe is None:
            pe = self.tconfig.environment
        try:
            return self._repositories[pe.eid]
        except KeyError:
            repdef = pe.apycot_repository_def
            repdef['branch'] = self.apycot_config().get('branch')
            apyrep = get_repository(repdef)
            self._repositories[pe.eid] = apyrep
            return apyrep

    def apycot_preprocessors(self, pe):
        try:
            return self._preprocessors[pe.eid]
        except KeyError:
            # turn {pp_type: pp_name} into  {pp_type: pp_instance}
            preprocessors = self._preprocessors[pe.eid] = {}
            for pptype, name in pe.apycot_preprocessors.items():
                options = options_from_dict(self.apycot_config(pe), name)
                ppfact = get_registered('preprocessor', name)
                preprocessors[pptype] = ppfact(self.writer, options)
            return preprocessors

    def project_path(self, subpath=False):
        if subpath and self.tconfig.subpath:
            return os.path.join(self.apycot_repository().co_path(),
                                self.tconfig.subpath)
        return self.apycot_repository().co_path()

    def checkout(self, pe):
        vcsrepo = self.apycot_repository(pe)
        cocmd = vcsrepo.co_command()
        if cocmd:
            Command(self.writer, cocmd, raises=True, shell=True).run()
        movebranchcmd = vcsrepo.co_move_to_branch_command()
        if movebranchcmd:
            Command(self.writer, movebranchcmd, shell=True).run()
        self.writer.link_to_revision(pe, vcsrepo)

    def setup(self):
        """setup the test environment"""
        self.resource_ctrl.setup_limit()
        skipmsg = "Unknown error during setup"
        try:
            # setup environment variables
            if self.environ:
                for key, val in self.environ.items():
                    self.update_env(self.tconfig.name, key, val)
            # checkout main package
            self.checkout(self.tconfig.environment)
            if 'install' in self.need_preprocessors:
                # checkout dependencies only if installation needed
                for dpe in self.tconfig.dependencies():
                    try:
                        self.checkout(dpe)
                    except SetupException, ex:
                        self._failed_pp.add('install')
                        continue
                    # run preprocessor against the dependency
                    self.call_preprocessor('install', dpe)
            for pptype in self.need_preprocessors:
                self.call_preprocessor(pptype, self.tconfig.environment,
                                       test=self)
        except:
            self._skip(self.checkers, skipmsg)
            raise
        finally:
            self.resource_ctrl.clean_limit()

    def call_preprocessor(self, pptype, penv, test=None):
        preprocessor = self.apycot_preprocessors(penv).get(pptype)
        if preprocessor is None:
            return
        path = self.apycot_repository(penv).co_path()
        self.writer.execution_info('run preprocessor %s on %s', pptype, path)
        try:
            if test is None:
                preprocessor.dependency_setup(self, path)
            else:
                preprocessor.test_setup(self)
        except Exception, ex:
            msg = '%s while running preprocessor %s: %s'
            self.writer.error(msg, ex.__class__.__name__, preprocessor.id, ex,
                              path=path, tb=True)
            self._failed_pp.add(pptype)

    def clean(self):
        """clean the test environment"""
        if self.archive:
            exec_id      = self.writer.exec_id()
            instance_id  = self._exec_options.get('cw_inst_id')
            archive_name = make_archive_name(instance_id, exec_id)
            archive_path = os.path.join(self.archive_dir, archive_name)
            tar_ball = tarfile.open(archive_path, ARCHIVE_MODE)
            tar_ball.add(self.tmpdir)
            tar_ball.close()
            self.writer.execution_info('Archive created at %s',
                                       archive_path)
            self.writer.raw(type="archive", name="Test directory archive name",
                            value=archive_name, check_data=False)
            # useless at the moment
            # self.writer.raw(type="archive", name="id",
            #                 value=exec_data['exec-id'], check_data=False)
        if not self.keep_test_dir:
            rmtree(self.tmpdir)
        else:
            self.writer.execution_info('temporary directory not removed: %s',
                                       self.tmpdir)

    def run(self):
        """run all checks in the test environment"""
        self.resource_ctrl.setup_limit()
        checkers = iter(self.checkers)
        skipmsg = "Unknown error in unknown check"
        try:
            writer = self.writer
            for checker in checkers:
                writer.start_check(checker.id, checker.options)
                if checker.need_preprocessor in self._failed_pp:
                    msg = 'Can\'t run checker %s: preprocessor %s have failed'
                    writer.fatal(msg, checker.id, checker.need_preprocessor)
                    writer.end_check(ERROR)
                    continue
                try:
                    try:
                        checker.check_options()
                    except ConfigError, ex:
                        msg = 'Config error for %s checker: %s'
                        writer.fatal(msg, checker.id, ex)
                        writer.end_check(ERROR)
                        continue
                    status = FAILURE
                    try:
                        status = checker.run(self)
                        self.executed_checkers[checker.id] = status
                    except RESOURCE_LIMIT_EXCEPTION:
                        raise
                    except Exception, ex:
                        msg = 'Error while running checker %s: %s'
                        writer.fatal(msg, checker.id, ex, tb=True)
                        status = ERROR
                    writer.end_check(status)
                    self.writer.execution_info('%s [%s]', checker.id, status)
                except ResourceError, ex:
                    skipmsg = '%s limit reached while running checker %s'
                    writer.fatal(skipmsg, ex.limit, checker.id)
                    writer.end_check(KILLED)
                    raise
                except MemoryError:
                    skipmsg = 'Memory limit reached while running checker %s'
                    writer.fatal(skipmsg, checker.id)
                    writer.end_check(KILLED)
                    raise
        finally:
            # nothing skipped if no checkers remaining
            self._skip(checkers, skipmsg)
            self.resource_ctrl.clean_limit()

    def _skip(self, checkers, skip_message):
        """mark all checkers as skipped for the 'skip_message reason'"""
        for checker in checkers:
            self.writer.start_check(checker.id, checker.options)
            msg = "%s checker didn't run because : %s"
            self.writer.error(msg, checker.id, skip_message)
            self.writer.end_check(SKIPPED)

    def execute(self):
        """setup, run and clean the test"""
        # FIXME keep compatibility with python2.4 in Debian stable (etch)
        # FIXME Feel free to use the 'with' statement afterwards.
        #with pushd(self.tmpdir):
        cwd = os.getcwd()
        os.chdir(self.tmpdir)
        try:
            try:
                self.writer.start_test(self.apycot_repository().branch)
                if self.keep_test_dir:
                    self.writer.raw('test directory', self.tmpdir)
                try:
                    # setup test
                    self.setup()
                    # run the test (which is actually a suite of test)
                    self.writer.set_exec_status(u'running tests')
                    self.run()
                except ResourceError, ex:
                    self.writer.fatal('%s resource limit reached, aborted', ex.limit)
                except MemoryError:
                    self.writer.fatal('memory resource limit reached, arborted')
                except Exception, ex:
                    self.writer.error('unexpected error', tb=True)
            finally:
                try:
                    self.writer.set_exec_status(u'cleaning')
                    self.clean()
                    self.writer.end_test(self.archive)
                except:
                    # XXX log error
                    pass
                self._cnx.close()
        finally:
            os.chdir(cwd)
