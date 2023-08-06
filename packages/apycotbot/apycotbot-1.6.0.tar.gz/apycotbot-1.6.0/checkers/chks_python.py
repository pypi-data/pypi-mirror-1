"""checkers for python source files

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import sys
import os
import re
from commands import getoutput
from os.path import join, exists, abspath, dirname
from test import test_support
from warnings import warn

from logilab.common.testlib import find_tests
from logilab.common.modutils import get_module_files
from logilab.common.fileutils import norm_read
from logilab.common.textutils import splitstrip
from logilab.common.decorators import cached
from logilab.common.compat import any

try:
    from logilab.devtools.lib.pkginfo import PackageInfo
    from logilab.devtools.__pkginfo__ import version as devtools_version
except ImportError:
    devtools_version = 'nc'

try:
    # development version
    from logilab.devtools.lib import coverage
    COVFILE = coverage.__file__.replace('.pyc', '.py')
except ImportError:
    try:
        # debian installed version
        import coverage
        COVFILE = coverage.__file__.replace('.pyc', '.py')
    except ImportError:
        coverage = None

from apycotbot import register
from apycotbot.utils import SUCCESS, FAILURE, PARTIAL, NODATA, ERROR
from apycotbot.utils import SimpleOutputParser, ParsedCommand
from apycotbot.checkers import BaseChecker, AbstractFilteredFileChecker


def pyinstall_path(test):
    path = _pyinstall_path(test)
    if not exists(path):
        raise Exception('path %s doesn\'t exist' %  path)
    return path

@cached
def _pyinstall_path(test):
    """return the project's installation path"""
    config = test.apycot_config()
    if 'install_path' in config:
        return config['install_path']
    modname = config.get('python_modname')
    if modname:
        return join(test.tmpdir, 'local', 'lib', 'python', *modname.split('.'))
    elif exists(join(test.project_path(), '__pkginfo__.py')):
        pkginfo = PackageInfo(directory=test.project_path())
        modname = getattr(pkginfo, 'modname', None)
        package = getattr(pkginfo, 'subpackage_of', None)
        if modname and package:
            modname = '%s.%s' % (package, modname)
        if modname:
            path = join(test.tmpdir, 'local', 'lib', 'python',
                        *modname.split('.'))
            if test.tconfig.subpath:
                path = join(path, test.tconfig.subpath)
        return path
    return abspath(test.project_path(subpath=True))

def pyversion_available(python):
    return not os.system('%s -V 2>/dev/null' % python)


class PythonSyntaxChecker(AbstractFilteredFileChecker):
    """check syntax of python file

       Use Pylint to check a score for python package. The check fails if the score is
       inferior to a given treshold.
    """

    id = 'python_syntax'
    checked_extensions = ('.py', )

    def check_file(self, filepath):
        """try to compile the given file to see if it's syntaxicaly correct"""
        # Try to compile it. If compilation fails, then there's a
        # SyntaxError
        try:
            compile(norm_read(filepath) + '\n', filepath, "exec")
            return SUCCESS
        except SyntaxError, error:
            self.writer.error(error.msg, path=filepath, line=error.lineno)
            return FAILURE

    def version_info(self):
        self.record_version_info('python', sys.version)

register('checker', PythonSyntaxChecker)


class PyTestParser(SimpleOutputParser):
    non_zero_status_code = FAILURE
    # search for following output:
    #
    # 'Ran 42 test cases in 0.07s (0.07s CPU), 3 errors, 31 failures, 3 skipped'
    regex = re.compile(
        r'Ran (?P<total>[0-9]+) test cases '
        'in (?P<time>[0-9]+(.[0-9]+)?)s \((?P<cputime>[0-9]+(.[0-9]+)?)s CPU\)'
        '(, )?'
        '((?P<errors>[0-9]+) errors)?'
        '(, )?'
        '((?P<failures>[0-9]+) failures)?'
        '(, )?'
        '((?P<skipped>[0-9]+) skipped)?'
        )

    total, failures, errors, skipped = 0, 0, 0, 0

    def _parse(self, stream):
        super(PyTestParser, self)._parse(stream)
        if self.total == 0:
            self.writer.error('File doesn\'t contains any test cases',
                              path=self.path)
            self.set_status(NODATA)
        elif self.errors or self.failures:
            self.set_status(FAILURE)
        elif self.skipped:
            self.set_status(PARTIAL)

    @property
    def success(self):
        return max(0, self.total - sum(( self.failures, self.errors,
                                         self.skipped,)))
    def add_junk(self, line):
        if any(c for c in line if c not in 'EF. \n\t\r-*'):
            self.unparsed.append(line)

    def extract_tests_status(self, values):
        for status in ('failures', 'errors', 'skipped'):
            try:
                setattr(self, status,
                        max(getattr(self, status), int(values[status])))
            except TypeError:
                pass

    def parse_line(self, line):
        match = self.regex.match(line)
        if match is not None:
            values = match.groupdict()
            self.total = int(values['total'])
            self.extract_tests_status(values)
            return
        self.add_junk(line)


class PyTestChecker(BaseChecker):
    """check that unit tests of a python package succeed using the pytest command
    (from logilab.common)
    """

    id = 'pytest'
    need_preprocessor = 'install'
    parsercls = PyTestParser
    parsed_content = 'stdout'
    options_def = [
        {'name': 'tested_python_versions', 'type': 'csv',
         'help': ('comma separated list of python version (such as 2.5) that '
                  'should be considered for testing.'),
         },
        {'name': 'ignored_python_versions', 'type': 'csv',
         'help': ('comma separated list of python version (such as 2.5) that '
                  'should be ignored for testing when '
                  'use_pkginfo_python_versions is set to 1.'),
         },
        {'name': 'use_pkginfo_python_versions', 'type': 'int',
         'help': ('0/1 flag telling if tested python version should be '
                  'determinated according to __pkginfo__.pyversion of the '
                  'tested project. This option is ignored if tested_python_versions '
                  'is set.'),
         },
        {'name': 'argument', 'type': 'string',
         'help': ('extra argument to give to pytest. Add this option multiple '
                  'times in the correct order to give several arguments.'),
         },
        ]

    def __init__(self, writer, options=None):
        BaseChecker.__init__(self, writer, options)
        self._path = None
        self.test = None

    @property
    @cached
    def pyversions(self):
        tested_pyversions = self.get_option("tested_python_versions", None)
        if tested_pyversions:
            pyversions = set(splitstrip(tested_pyversions))
        elif int(self.get_option("use_pkginfo_python_versions", True)):
            try:
                pkginfodir = dirname(self.test.environ['pkginfo'])
            except KeyError:
                pkginfodir = self.test.project_path()
            try:
                pkginfo = PackageInfo(directory=pkginfodir)
                pyversions = set(pkginfo.pyversions)
            except (NameError, ImportError):
                pyversions = set()
            ignored_pyversions = self.get_option("ignored_python_versions", None)
            if ignored_pyversions:
                ignored_pyversions = set(splitstrip(ignored_pyversions))
                ignored_pyversions = pyversions.intersection(
                    ignored_pyversions)
                if ignored_pyversions:
                    for py_ver in ignored_pyversions:
                        self.writer.debug("python version %s ignored", py_ver)
                    pyversions.difference_update(ignored_pyversions)
        else:
            pyversions = None
        if pyversions:
            pyversions = ['python%s' % pyver for pyver in pyversions]
            pyversions_ = [python for python in pyversions
                           if pyversion_available(python)]
            if len(pyversions) > len(pyversions_):
                for pyver in pyversions:
                    if not pyver in pyversions:
                        self.writer.error('config asked for %s, but it\'s not available', pyver)
            pyversions = pyversions_
        else:
            pyversions = [sys.executable]
        return pyversions

    def version_info(self):
        if self.pyversions:
            self.record_version_info('python', ', '.join(self.pyversions))

    def coverage_enabled(self):
        return coverage is not None and self._coverage is not None

    def _run(self, test):
        """run the checker against <path> (usually a directory)"""
        test_support.verbose = 0
        self.test = test
        if not self.pyversions:
            self.writer.error('no required python version available')
            return ERROR
        for checker in test.checkers:
            if checker.id == 'pycoverage':
                self._coverage = checker
                break
        else:
            self._coverage = None
        return self._start_unittest()

    def _start_unittest(self):
        if self.coverage_enabled():
            self._coverage.coverage_data_dir = pyinstall_path(self.test)
            command = ['-c', 'from logilab.common.pytest import run; import sys; sys.argv=["pytest", "--coverage"]; run()']
        else:
            command = ['-c', 'from logilab.common.pytest import run; run()']
        extraargs = self.get_option("argument", [])
        if not isinstance(extraargs, list):
            command.apend(extraargs)
        else:
            command += extraargs
        cwd = os.getcwd()
        os.chdir(pyinstall_path(self.test))
        try:
            status = SUCCESS
            testresults = {'success': 0, 'failures': 0,
                           'errors': 0, 'skipped': 0}
            total = 0
            for python in self.pyversions:
                cmd = self.run_test(command, python)
                for rtype in testresults:
                    total += getattr(cmd.parser, rtype)
                    testresults[rtype] += getattr(cmd.parser, rtype)
                status = self.merge_status(status, cmd.status)
            self.execution_info(total, testresults)
            return status
        finally:
            os.chdir(cwd)

    def execution_info(self, total, testresults):
        self.writer.raw('total_test_cases', total, 'result')
        self.writer.raw('succeeded_test_cases', testresults['success'], 'result')
        self.writer.raw('failed_test_cases', testresults['failures'], 'result')
        self.writer.raw('error_test_cases', testresults['errors'], 'result')
        self.writer.raw('skipped_test_cases', testresults['skipped'], 'result')

    def get_command(self, command, python):
        return [python, '-W', 'ignore'] + command

    def run_test(self, command, python='python'):
        """execute the given test file and parse output to detect failed /
        succeed test cases
        """
        if isinstance(command, basestring):
            command = [command]
        command = self.get_command(command, python)
        cmd = ParsedCommand(self.writer, command,
                            parsercls=self.parsercls,
                            parsed_content=self.parsed_content,
                            path=self._path)
        #cmd.parser.path = join(self._path, command[0]) # XXX
        cmd.run()
        return cmd

register('checker', PyTestChecker)


class PyUnitTestParser(PyTestParser):
    result_regex = re.compile(
        r'(OK|FAILED)'
        '('
        ' \('
        '(failures=(?P<failures>[0-9]+))?'
        '(, )?'
        '(errors=(?P<errors>[0-9]+))?'
        '(, )?'
        '(skipped=(?P<skipped>[0-9]+))?'
        '\)'
        ')?')

    total_regex = re.compile(
        'Ran (?P<total>[0-9]+) tests?'
        ' in (?P<time>[0-9]+(.[0-9]+)?s)')

    def parse_line(self, line):
        match = self.total_regex.match(line)
        if match is not None:
            self.total = int(match.groupdict()['total'])
            return
        match = self.result_regex.match(line)
        if match is not None:
            self.extract_tests_status(match.groupdict())
            return
        self.add_junk(line)


class PyUnitTestChecker(PyTestChecker):
    """check that unit tests of a python package succeed

    Execute tests found in the "test" or "tests" directory of the package. The
    check succeed if no test cases failed. Note each test module is executed by
    a spawed python interpreter and the output is parsed, so tests should use
    the default text output of the unittest framework, and avoid messages on
    stderr.

    spawn unittest and parse output (expect a standard TextTestRunner)
    """

    id = 'pyunit'
    parsed_content = 'stderr'
    parsercls = PyUnitTestParser
    options_def = PyTestChecker.options_def[:-1] + [
        {'name': 'test_dirs', 'type': 'csv',
         'help': ('comma separated list of directories where tests could be '
                  'find. Search in "test" and "tests by default.'),
         },
        ]

    def _start_unittest(self):
        status = SUCCESS
        testdirs = splitstrip(self.get_option("test_dirs", 'test,tests'))
        basepath = self.test.project_path(subpath=True)
        for testdir in testdirs:
            testdir = join(basepath, testdir)
            if exists(testdir):
                self._path = testdir
                if self._coverage is not None:
                    self._coverage.coverage_data_dir = pyinstall_path(self.test)
                # FIXME keep compatibility with python2.4 in Debian stable (etch)
                # FIXME Feel free to use the 'with' statement afterwards.
                #with pushd(testdir):
                cwd = os.getcwd()
                os.chdir(testdir)
                try:
                    _status = self.run_tests()
                    status = self.merge_status(status, _status)
                finally:
                    os.chdir(cwd)
                break
        else:
            self.writer.error('no test directory', path=basepath)
            status = NODATA
        return status

    def run_tests(self):
        """run a package test suite
        expect to be in the test directory
        """
        tests = find_tests('.')
        if not tests:
            self.writer.error('no test found', path=self._path)
            return NODATA
        status = SUCCESS
        testresults = {'success': 0, 'failures': 0,
                      'errors': 0, 'skipped': 0}
        total = 0
        for python in self.pyversions:
            for test_file in tests:
                cmd = self.run_test(test_file + '.py', python)
                for rtype in testresults:
                    total += getattr(cmd.parser, rtype)
                    testresults[rtype] += getattr(cmd.parser, rtype)
                status = self.merge_status(status, cmd.status)
        self.execution_info(total, testresults)
        return status

    def get_command(self, command, python):
        if self.coverage_enabled():
            return [python, '-W', 'ignore',  COVFILE, '-x',
                    '-p', pyinstall_path(self.test)] + command
        return [python, '-W', 'ignore'] + command


register('checker', PyUnitTestChecker)


class PyDotTestParser(PyUnitTestParser):
    line_regex = re.compile(
            r'(?P<filename>\w+\.py)(\[(?P<ntests>\d+)\] | - )(?P<results>.*)')
    success = 0
    def _parse(self, stream):
        for testname, _, _, results in self.line_regex.findall(stream.read()):
            if results == "FAILED TO LOAD MODULE":
                self.errors += 1
            else:
                self.success += results.count('.')
                self.failures += results.count('F')
                self.errors += results.count('E')
                self.skipped += results.count('s')


class PyDotTestChecker(PyUnitTestChecker):
    """check that py.test based unit tests of a python package succeed

    spawn py.test and parse output (expect a standard TextTestRunner)
    """
    need_preprocessor = 'install'
    id = 'py.test'
    parsercls = PyDotTestParser
    parsed_content = 'stdout'

    def get_command(self, command, python):
        # XXX coverage
        return ['py.test', '--exec=%s' % python, '--nomagic', '--tb=no'] + command

register('checker', PyDotTestChecker)


class PyLintChecker(BaseChecker):
    """check that the python package as a decent pylint evaluation
    """
    need_preprocessor = 'install'
    id = 'pylint'
    options_def = [
        {'name': 'threshold', 'type': 'int',
         'help': ('integer between 1 and 10 telling expected pylint note to '
                  'pass this check. Default to 7.'),
         },
        {'name': 'pylintrc',
         'help': ('path to a pylint configuration file.'),
         },
        {'name': 'show_categories', 'type': 'csv',
         'help': ('comma separated list of pylint message categories to add to '
                  'reports. Default to error (E) and failure (F).'),
         },
        {'name': 'additional_builtins',
         'help': ('comma separated list of additional builtins to give to '
                  'pylint.'),
         },
        {'name': 'disable_msg',
         'help': ('comma separated list of pylint message id that should be '
                  'ignored.'),
         },
        ] + AbstractFilteredFileChecker.options_def

    def version_info(self):
        self.record_version_info('pylint', pylint_version)

    def _run(self, test):
        """run the checker against <path> (usually a directory)"""
        threshold = int(self.get_option('threshold', 7))
        pylintrc_path = self.get_option('pylintrc', None)
        linter = PyLinter(pylintrc=pylintrc_path)
        linter.set_option('persistent', False)
        linter.set_option('reports', 0, action='store')
        linter.quiet = 1
        # register checkers
        checkers.initialize(linter)
        # load configuration
        package_wd_path = test.project_path()
        if exists(join(package_wd_path, 'pylintrc')):
            linter.load_file_configuration(join(package_wd_path, 'pylintrc'))
        else:
            linter.load_file_configuration()
        # set file or dir to ignore
        for option in ('ignore', 'additional_builtins', 'disable_msg'):
            try:
                value = getattr(self, '%s_option' % option)()
            except AttributeError:
                value = self.get_option(option, None)
            if value is not None:
                linter.global_set_option(option.replace('_', '-'), ','.join(value))
        # message categories to record
        categories = self._csv_option('show_categories', ('E', 'F'))
        linter.set_reporter(MyLintReporter(self.writer, test.tmpdir, categories))
        # run pylint
        linter.check(pyinstall_path(test))
        try:
            note = eval(linter.config.evaluation, {}, linter.stats)
            self.writer.raw('pylint_evaluation', '%.2f' % note, 'result')
        except ZeroDivisionError:
            self.writer.raw('pylint_evaluation', '0', 'result')
            note = 0
        except Exception, ex:
            self.writer.error('Error while processing pylint evaluation',
                              path=test.project_path(subpath=True), tb=True)
            note = 0
        self.writer.raw('statements', '%i' % linter.stats['statement'], 'result')
        if note < threshold:
            return FAILURE
        return SUCCESS

    def additional_builtins_option(self):
        """return <additional_builtins> option value"""
        return self._csv_option('additional_builtins')

    def disable_msg_option(self):
        """return <disable_msg> option value"""
        return self._csv_option('disable_msg')

    def _csv_option(self, optname, default=None):
        """return the <optname> options value or default if not defined
        """
        value = self.get_option(optname, None)
        if value is not None:
            value = splitstrip(value)
        else:
            value = default
        return value

try:
    from pylint import checkers
    from pylint.lint import PyLinter
    from pylint.__pkginfo__ import version as pylint_version
    from pylint.interfaces import IReporter
    register('checker', PyLintChecker)

    class MyLintReporter(object):
        """a partial pylint writer (implements only the message method, not
        methods necessary to display layouts
        """
        __implements__ = IReporter

        def __init__(self, writer, basepath, categories):
            self.writer = writer
            self.categories = set(categories)
            self._to_remove = len(basepath) + 1 # +1 for the leading "/"

        def add_message(self, msg_id, location, msg):
            """ manage message of different type and in the context of path """
            if not msg_id[0] in self.categories:
                return
            path, line = location[0], location[-1]
            path = path[self._to_remove:]
            if msg_id[0] == 'I':
                self.writer.info(msg, path=path, line=line)
            elif msg_id[0]  == 'E':
                self.writer.error(msg, path=path, line=line)
            elif msg_id[0] == 'F':
                self.writer.fatal(msg, path=path, line=line)
            else: # msg_id[0] in ('R', 'C', 'W')
                self.writer.warning(msg, path=path, line=line)

        def display_results(self, layout):
            pass
except ImportError, e:
    warn("unable to import pylint. Pylint checker disabled : %s" % e)


class PyCoverageChecker(BaseChecker):
    """check the tests coverage of a python package

    if used, it must be after the pyunit checker

    When devtools is available, test will be launched in a coverage mode. This
    test will gather coverage information, and will succeed if the test coverage
    is superior to a given treshold. *This checker must be executed after the
    python_unittest checker.
    """

    id = 'pycoverage'
    options_def = [
        {'name': 'threshold', 'type': 'int',
         'help': ('integer between 1 and 100 telling expected percent coverage '
                  'to pass this check. Default to 80.'),
         },
        ]
    coverage_data_dir = None # set by the checker generating coverage data

    def version_info(self):
        self.record_version_info('devtools', devtools_version)

    def _run(self, test):
        """run the checker against <path> (usually a directory)"""
        threshold = int(self.get_option('threshold', 80))
        assert threshold, 'no threshold defined'
        # XXX check the pyunit check is executed before (with coverage
        # activated) ?
        if os.environ.get('COVERAGE_FILE'):
            percent = self._get_cover_info(pyinstall_path(test))
        else:
            if not self.coverage_data_dir:
                self.writer.error('no coverage information generated')
                return NODATA
            # FIXME keep compatibility with python2.4 in Debian stable (etch)
            # FIXME Feel free to use the 'with' statement afterwards.
            #with pushd(testdir):
            cwd = os.getcwd()
            os.chdir(self.coverage_data_dir)
            try:
                if not exists('.coverage'):
                    self.writer.error('no coverage information',
                                      path=self.coverage_data_dir)
                    return NODATA
                percent = self._get_cover_info(pyinstall_path(test))
            finally:
                os.chdir(cwd)
        if percent < threshold:
            return FAILURE
        return SUCCESS

    def _get_cover_info(self, inst_path):
        covertool = coverage.Coverage()
        covertool.restore()
        stats = covertool.report_stat(inst_path, ignore_errors=1)
        percent = stats[coverage.TOTAL_ENTRY][2]
        self.writer.raw('coverage', '%.3f' % (percent, ), 'result')
        result = []
        for name in stats.keys():
            if name == coverage.TOTAL_ENTRY:
                continue
            nb_stmts, nb_exec_stmts, pc, pc_missing, readable = stats[name]
            if pc == 100:
                continue
            result.append( (pc_missing, name, pc, readable) )
        result.sort()
        for _, name, pc_cover, readable in result:
            msg = '%d %% covered, missing %s' % (pc_cover, readable)
            self.writer.info(msg, path=name)
        return percent

if coverage is not None:
    register('checker', PyCoverageChecker)


class PyCheckerOutputParser(SimpleOutputParser):
    non_zero_status_code = FAILURE
    def parse_line(self, line):
        try:
            path, line, msg = line.split(':')
            self.writer.error(msg, path=path, line=line)
            self.status = FAILURE
        except ValueError:
            self.unparsed.append(line)

class PyCheckerChecker(BaseChecker):
    """check that unit tests of a python package succeed

    spawn unittest and parse output (expect a standard TextTestRunner)
    """

    id = 'pychecker'
    need_preprocessor = 'install'

    def _run(self, test):
        """run the checker against <path> (usually a directory)"""
        command = ['pychecker', '-Qqe', 'Style']
        command += get_module_files(pyinstall_path(test))
        return ParsedCommand(self.writer, command, parsercls=PyCheckerOutputParser).run()

    def version_info(self):
        self.record_version_info('pychecker', getoutput("pychecker --version").strip())

register('checker', PyCheckerChecker)
