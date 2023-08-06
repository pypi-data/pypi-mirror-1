import shutil
import os
from os.path import exists, join, abspath

from logilab.common.testlib import TestCase, unittest_main, mock_object

from utils import MockWriter, MockRepository, MockConnection, input_path

from apycotbot import SetupException
from apycotbot.utils import SUCCESS, FAILURE, PARTIAL, SKIPPED
from apycotbot.task import Test as BaseTest, ApycotTask
from apycotbot.repositories import FSRepository

def Test(*args, **kwargs):
    pps = kwargs.pop('preprocessors', None)
    checkers = kwargs.pop('checkers', None)
    repo = kwargs.pop('repo', MOCKREPO)
    test = BaseTest(*args, **kwargs)
    if pps is not None:
        test.apycot_preprocessors = lambda x: pps
    if checkers is not None:
        test.checkers = checkers
        test.need_preprocessors = set(chk.need_preprocessor for chk in checkers
                                      if chk.need_preprocessor is not None)
    if repo is not None:
        test._repositories[test.tconfig.environment.eid] = repo
    return test

class TestConfig:
    def __init__(self, name, dependencies=(), environ=None):
        self.name = self.eid = name
        #self._repo = repo
        self._dependencies = dependencies
        self._environ = environ or {'ZIGUOUIGOUI': 'YOOOO'}
        self.environment = mock_object(eid=name, apycot_preprocessors={})
        self.all_checks = ()
    @property
    def apycot_configuration(self):
        return {}
    @property
    def apycot_process_environment(self):
        return self._environ

    def dependencies(self):
        return self._dependencies

# mock objects ################################################################

class CleanRaisePreprocessor:
    id = 'clean_raise_preprocessor'
    def match(self, name):
        return 1

    def dependency_setup(self, test, path):
        return 0

    def test_setup(self, test):
        return 1

class SetupRaisePreprocessor:
    id = 'setup_raise_preprocessor'
    def match(self, name):
        return 1

    def dependency_setup(self, test, path):
        raise SetupException('%s failed on %r' % (self.id, path))

    def test_setup(self, test):
        raise SetupException('in test_preprocessor.test_setup')

class TouchTestPreprocessor:
    id = 'touch_preprocessor'
    file = None

    def test_setup(self, test):
        self.file = join(test.tmpdir, 'TestTC_pp')
        self.file2 = join(test.tmpdir, 'TestTC2_pp')
        f = open(self.file, 'w')
        f.close()
        f = open(self.file2, 'w')
        f.close()


class DummyTest(object):
    need_preprocessor = None

    def run(self, test, writer):
        return SUCCESS
    def check_options(self):
        pass

class SuccessTestChecker(DummyTest):
    id = 'success_test_checker'
    options = {}
    need_preprocessor = 'install'
    def run(self, test, writer):
        return SUCCESS

class FailureTestChecker(DummyTest):
    id = 'failure_test_checker'
    options = {}
    def run(self, test, writer):
        return FAILURE

class ErrorTestChecker(DummyTest):
    id = 'error_test_checker'
    options = {}
    def run(self, test, writer):
        raise Exception('never succeed!')


# real tests ##################################################################

MOCKREPO = MockRepository(repository='/home/cvs',
                          path='soft/goodpkg',
                          command='cp -R %s .' % input_path('goodpkg'))
BADREPO = MockRepository(repository='/home/cvs',
                         path='soft/goodpkg', command='false')
FSREPO1 = FSRepository({'repository': input_path('goodpkg')})
FSREPO2 = FSRepository({'repository': input_path('badpkg2')})
WRITER = MockWriter()
CONN = MockConnection()
TPP = TouchTestPreprocessor()

class TestTC(TestCase):

    def test_str(self):
        command = 'cp -R '+abspath('data/goodpkg')+' .'
        test = Test(CONN, TestConfig('yo'), None, {})
        self.assertEquals(str(test), "<MockRepository {'path': 'soft/goodpkg', 'command': '%s', 'repository': '/home/cvs'}>" % command)

    def test_setup_no_install(self):
        test = Test(CONN, TestConfig('yo', dependencies=(TestConfig('pypasax'),)),
                    WRITER, {},
                    preprocessors={'install': TPP})
        test._repositories['pypasax'] = FSREPO2
        # no checks requiring installation, main repo should be checked out though not installed,
        # and dependencies shouldn't be installed
        try:
            test.setup()
            self.assertEquals(os.environ['ZIGUOUIGOUI'], 'YOOOO')
            self.failUnless(exists('goodpkg'))
            self.failIf(exists('badpkg2'))
            self.failUnless(TPP.file is None or not exists(TPP.file))
        finally:
            os.environ.pop('ZIGUOUIGOUI', None)
            shutil.rmtree('goodpkg')

    def test_python_setup(self):
        test = Test(CONN, TestConfig('yo', dependencies=(TestConfig('pypasax'),)),
                    WRITER, {},
                    checkers=[SuccessTestChecker()],
                    preprocessors={'install': TPP})
        test._repositories['pypasax'] = FSREPO2
        try:
            test.setup()
            self.assertEquals(os.environ['ZIGUOUIGOUI'], 'YOOOO')
            self.failUnless(exists('goodpkg'))
            self.failUnless(exists('badpkg2'))
            self.failUnless(exists(TPP.file))
        finally:
            shutil.rmtree('goodpkg')
            shutil.rmtree('badpkg2')
            os.remove(TPP.file)
            os.remove(TPP.file2)
            del os.environ['ZIGUOUIGOUI']

    def _test_setup_ex(self, test, msg=None):
        try:
            cwd = os.getcwd()
            os.chdir(test.tmpdir)
            try:
                test.setup()
                self.failUnless(test._failed_pp)
            except SetupException, ex:
                if msg:
                    self.assertEquals(str(ex), msg)
        finally:
            shutil.rmtree(test.tmpdir)
            os.chdir(cwd)

    def test_setup_raise(self):
        # test bad checkout command
        test = Test(CONN, TestConfig('yo'), WRITER, {}, repo=BADREPO)
        self._test_setup_ex(test, "`false` returned with status : 1")
        # test bad dependencies checkout
        test = Test(CONN, TestConfig('yo',
                                     dependencies=(TestConfig('toto'),),
                                     ),
                    WRITER, {},
                    checkers=[SuccessTestChecker()])
        test._repositories['toto'] = BADREPO
        self._test_setup_ex(test)
        # test bad preprocessing
        test = Test(CONN, TestConfig('yo',
                                     dependencies=(TestConfig('pypasax'),),
                                     ),
                    WRITER, {},
                    checkers=[SuccessTestChecker()],
                    preprocessors={'install': SetupRaisePreprocessor()})
        test._repositories['pypasax'] = FSREPO2
        self._test_setup_ex(test)

    def test_clean(self):
        test = Test(CONN, TestConfig('yo', dependencies=(TestConfig('pypasax'),),
                                     ),
                    WRITER, {},
                    checkers=[SuccessTestChecker()],
                    preprocessors={'install': TPP})
        test._repositories['pypasax'] = FSREPO2
        # clean should never fail
        # but most interesting things occurs after setup...
        test.execute()
        self.failIf(exists('goodpkg'))
        self.failIf(exists('badpkg2'))
        self.failIf(exists(TPP.file))

    def test_execute_1(self):
        test = Test(CONN, TestConfig('yo', dependencies=(TestConfig('Pypasax'),),
                                     ),
                    WRITER, {}, repo=FSREPO1,
                    checkers=[SuccessTestChecker(), FailureTestChecker(), ErrorTestChecker()],
                    preprocessors={'install': TPP})
        test._repositories['Pypasax'] = FSREPO2
        test.execute()
        self.failIf(exists(TPP.file))
        self.failIf(exists(TPP.file2))

    def test_execute_2(self):
        test = Test(CONN, TestConfig('yo', dependencies=(TestConfig('Pypasax', FSREPO2),),
                                     ),
                    WRITER, {}, repo=FSREPO1,
                    checkers=[SuccessTestChecker(), FailureTestChecker(), ErrorTestChecker()],
                    preprocessors={'install:': SetupRaisePreprocessor()})
        test._repositories['Pypasax'] = FSREPO2
        test.execute()

    def test_execute_0(self):
        command = 'cp -R '+abspath('inputs/goodpkg')+' .'
        cwd = os.getcwd()
        test = Test(CONN, TestConfig('yo', dependencies=(TestConfig('Pypasax'),)),
                    WRITER, {})
        test._repositories['Pypasax'] = FSREPO2
        self.failUnless(exists(test.tmpdir))
        test.execute()
        self.failIf(exists(test.tmpdir))
        self.assertEquals(os.getcwd(), cwd)

        test = Test(CONN, TestConfig('yo', dependencies=(TestConfig('Pypasax'),)),
                    WRITER, {'keep-test-dir':1},)
        test._repositories['Pypasax'] = FSREPO2
        self.failUnless(exists(test.tmpdir))
        test.execute()
        self.failIf(exists(test.tmpdir))
        self.assertEquals(os.getcwd(), cwd)

        test = Test(CONN, TestConfig('yo', dependencies=(TestConfig('Pypasax'),),
                                     ),
                    WRITER, {}, repo=FSREPO1,
                    checkers=[SuccessTestChecker()],
                    preprocessors={'install': SetupRaisePreprocessor()})
        test._repositories['Pypasax'] = FSREPO2
        self.failUnless(exists(test.tmpdir))
        test.execute()
        self.failIf(exists(test.tmpdir))
        self.assertEquals(os.getcwd(), cwd)

        test = Test(CONN, TestConfig('yo', dependencies=(TestConfig('Pypasax'),),
                                     ),
                    WRITER, {}, repo=FSREPO1,
                    checkers=[SuccessTestChecker()],
                    preprocessors={'install': CleanRaisePreprocessor()})
        test._repositories['Pypasax'] = FSREPO2
        self.failUnless(exists(test.tmpdir))
        test.execute()
        self.failIf(exists(test.tmpdir))
        self.assertEquals(os.getcwd(), cwd)


class TaskTC(TestCase):
    def test_serialized_command(self):
        t = ApycotTask(1234, 'an env', 'a config')
        self.assertEquals(t.run_command(mock_object(options={})),
                          ['apycotclient', 'run',
                           '--cw-inst-id=system',
                           'an env', 'a config'])


if __name__ == '__main__':
    unittest_main()
