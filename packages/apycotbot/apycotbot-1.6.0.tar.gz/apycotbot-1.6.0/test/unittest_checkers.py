"""
unit tests for checkers
"""

from logilab.common.testlib import unittest_main, TestCase
import unittest
import sys
import os
from os.path import join
zope_path = os.environ.get('SOFTWARE_HOME', '/usr/lib/zope/lib/python')
sys.path.insert(1, zope_path)

from unittest import TestSuite

from apycotbot.utils import SUCCESS, FAILURE, PARTIAL, NODATA, ERROR
from apycotbot.checkers.chks_python import *
from apycotbot.checkers.chks_xml import *
from apycotbot.checkers.chks_rest import *
from apycotbot.checkers.chks_pkg import *
from apycotbot.checkers import chks_pt

from utils import *

WRITER = MockWriter()


class FileCheckerTest(TestCase):
    def __init__(self, checker, files, method_name):
        TestCase.__init__(self, method_name)
        self.checker = checker
        self.files = [input_path(file) for file in files]

    def check_file(self,file):
        return self.checker.check_file(file)

    def check_dir(self,file):
        return self.checker.run(MockTest(MockRepository(path=file)))

    def chks_test_(self, expected, func):
        for file in self.files:
            status = func(file)
            msg = '%s on %s status: %s expecting %s' % (self.checker.id, file, status, expected)
            if self.checker.options:
                msg = '\n    '.join([msg] + ['='.join(str(i) for i in pair) for pair in self.checker.options.iteritems()])
            self.failUnlessEqual(status, expected, msg)#+'\n-----\n'+WRITER.stderr.getvalue())

    def chks_test_file_success(self):
        self.chks_test_(SUCCESS, self.check_file)

    def chks_test_file_failure(self):
        self.chks_test_(FAILURE, self.check_file)

    def chks_test_file_error(self):
        self.chks_test_(ERROR, self.check_file)

    def chks_test_dir_success(self):
        self.chks_test_(SUCCESS, self.check_dir)

    def chks_test_dir_failure(self):
        self.chks_test_(FAILURE, self.check_dir)

    def chks_test_dir_partial(self):
        self.chks_test_(PARTIAL, self.check_dir)

    def chks_test_dir_nodata(self):
        self.chks_test_(NODATA, self.check_dir)

    def chks_test_dir_error(self):
        self.chks_test_(ERROR, self.check_dir)


class ModuleCheckerTest(FileCheckerTest):

    def check_pkg(self, file):
        return self.checker.run(MockTest(MockRepository(path=file)))

    def chks_test_success(self):
        self.chks_test_(SUCCESS, self.check_pkg)

    def chks_test_error(self):
        self.chks_test_(ERROR, self.check_pkg)

    def chks_test_failure(self):
        self.chks_test_(FAILURE, self.check_pkg)

    def chks_test_partial(self):
        self.chks_test_(PARTIAL, self.check_pkg)

    def chks_test_nodata(self):
        self.chks_test_(NODATA, self.check_dir)


def suite():
    """return the unitest suite"""
    testsuite = TestSuite()
    addTest = testsuite.addTest
    ##### FileChecker #####

    file_checker = PythonSyntaxChecker(WRITER)
    addTest(FileCheckerTest(file_checker, ['empty_dir'], 'chks_test_dir_nodata'))

    ##### PythonSyntaxChecker #####
    python_syntax = PythonSyntaxChecker(WRITER)
    addTest(FileCheckerTest(python_syntax, ['goodsyntax.py'], 'chks_test_file_success'))
    addTest(FileCheckerTest(python_syntax, ['badsyntax.py'], 'chks_test_file_failure'))
    addTest(FileCheckerTest(python_syntax, ['goodsyntax/'], 'chks_test_dir_success'))
    addTest(FileCheckerTest(python_syntax, ['badsyntax/'], 'chks_test_dir_failure'))
    addTest(FileCheckerTest(python_syntax, ['mixedsyntax/'], 'chks_test_dir_failure'))
    addTest(FileCheckerTest(python_syntax, ['extentionfilter/'], 'chks_test_dir_success'))
    addTest(FileCheckerTest(python_syntax, ['syntax_dir/badsyntax/'], 'chks_test_dir_failure'))


    addTest(FileCheckerTest(python_syntax, ['goodsyntax.py'], 'chks_test_file_success'))

    python_syntax = PythonSyntaxChecker(WRITER, {'ignore':'wrongsyntax.py'})
    addTest(FileCheckerTest(python_syntax, ['syntax_dir/badsyntax/'], 'chks_test_dir_success'))

    python_syntax = PythonSyntaxChecker(WRITER, {'ignore':'rootbadsyntax.py,badsyntax'})
    addTest(FileCheckerTest(python_syntax, ['syntax_dir/'], 'chks_test_dir_success'))

    python_syntax = PythonSyntaxChecker(WRITER)
    python_syntax.best_status = 'partial'
    addTest(FileCheckerTest(python_syntax, ['extentionfilter/'], 'chks_test_dir_partial'))

    ##### PyUnitTestChecker #####
    python_unit = PyUnitTestChecker(WRITER)
    addTest(ModuleCheckerTest(python_unit, ['goodpkg'], 'chks_test_success'))
    addTest(ModuleCheckerTest(python_unit, ['badpkg1'], 'chks_test_nodata'))
    addTest(ModuleCheckerTest(python_unit, ['badpkg2'], 'chks_test_failure'))

    python_unit = PyUnitTestChecker(WRITER, {'test_dirs':'dir_for_tetsing'}) # typo is intentional#
    addTest(ModuleCheckerTest(python_unit, ['test_dirs_test_pkg/'], 'chks_test_success'))

    # use sys.executable, success
    python_unit = PyUnitTestChecker(WRITER, {'use_pkginfo_python_versions': '0'})
    addTest(ModuleCheckerTest(python_unit, ['goodpkg2.4/'], 'chks_test_success'))
    # py 2.4 & py 2.5, success
    python_unit = PyUnitTestChecker(WRITER, {'use_pkginfo_python_versions': '1'})
    addTest(ModuleCheckerTest(python_unit, ['goodpkg2.4/'], 'chks_test_success'))
    # use sys.executable, success
    python_unit = PyUnitTestChecker(WRITER, {'ignored_python_versions':'2.4'})
    addTest(ModuleCheckerTest(python_unit, ['goodpkg2.4/'], 'chks_test_success'))
    # unavailable py 2.3, error (ignored_python_versions option ignored when tested_python_versions is set)
    python_unit = PyUnitTestChecker(WRITER, {'ignored_python_versions':'2.3', 'tested_python_versions':'2.3'})
    addTest(ModuleCheckerTest(python_unit, ['goodpkg2.4/'], 'chks_test_error'))
    python_unit = PyUnitTestChecker(WRITER, {'tested_python_versions':'2.3', 'use_pkginfo_python_versions':'0'})
    addTest(ModuleCheckerTest(python_unit, ['goodpkg2.4/'], 'chks_test_error'))

    ##### PyCoverageChecker #####

    python_chks_test_coverage = PyCoverageChecker(WRITER, {'threshold': '1'})
    python_chks_test_coverage.coverage_data_dir = input_path('goodpkg/tests')
    addTest(ModuleCheckerTest(python_chks_test_coverage, ['goodpkg'], 'chks_test_success'))

    ##### PyLintChecker #####
    pylint = PyLintChecker(WRITER, {'threshold': 7})
    addTest(ModuleCheckerTest(pylint, ['pylint_ok.py'], 'chks_test_success'))
    addTest(ModuleCheckerTest(pylint, ['pylint_bad.py'], 'chks_test_failure'))

    pylint_rc = PyLintChecker(WRITER, {'threshold': 7,'pylintrc':input_path("pylintrc")})
    addTest(ModuleCheckerTest(pylint_rc, ['pylint_bad.py'], 'chks_test_success'))

    xml_syntax = XmlFormChecker(WRITER)
    addTest(FileCheckerTest(xml_syntax, ['invalid.xml'], 'chks_test_file_success'))
    addTest(FileCheckerTest(xml_syntax, ['malformed.xml'], 'chks_test_file_failure'))

    xml_valid = XmlValidChecker(WRITER, {'catalog': join(INPUTS_DIR,'logilab.cat')})
    addTest(FileCheckerTest(xml_valid, ['invalid.xml'], 'chks_test_file_failure'))

    rest_syntax = ReSTChecker(WRITER)
    addTest(FileCheckerTest(rest_syntax, ['goodrest.txt'], 'chks_test_file_success'))
    addTest(FileCheckerTest(rest_syntax, ['goodrest_2.txt'], 'chks_test_file_success'))
    addTest(FileCheckerTest(rest_syntax, ['goodrest_3.txt'], 'chks_test_file_success'))
    addTest(FileCheckerTest(rest_syntax, ['badrest.txt'], 'chks_test_file_failure'))
    addTest(FileCheckerTest(rest_syntax, ['badrest_2.txt'], 'chks_test_file_failure'))
    if hasattr(chks_pt, 'ZopePageTemplate'):
        pt_syntax = chks_pt.ZPTChecker(WRITER)
        addTest(FileCheckerTest(pt_syntax, ['task_view.pt'], 'chks_test_file_success'))
        addTest(FileCheckerTest(pt_syntax, ['task_view_bad.pt'], 'chks_test_file_failure'))

    pkg_doc = PackageDocChecker(WRITER)
    addTest(ModuleCheckerTest(pkg_doc, ['goodpkg'],'chks_test_success'))
    addTest(ModuleCheckerTest(pkg_doc, ['badpkg2'], 'chks_test_failure'))

    if not os.system('which py.test'):
        py_test = PyDotTestChecker(WRITER)
        addTest(ModuleCheckerTest(py_test, ['py_test/goodpkg'], 'chks_test_success'))
        addTest(ModuleCheckerTest(py_test, ['py_test/badpkg'], 'chks_test_failure'))

    return testsuite

if __name__ == '__main__':
    unittest_main()
