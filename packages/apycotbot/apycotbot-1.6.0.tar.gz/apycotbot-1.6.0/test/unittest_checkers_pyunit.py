"""
unit tests for python test checkers
"""

import os, sys
from os.path import join

from logilab.common.testlib import unittest_main, TestCase, mock_object

from apycotbot.utils import SUCCESS, FAILURE, ERROR, PARTIAL
from apycotbot.checkers import chks_python

from utils import MockWriter, input_path

def _test_cmd(self, cmd, status, success=0, failures=0, errors=0, skipped=0):
    self.assertEquals(cmd.parser.success, success)
    self.assertEquals(cmd.parser.failures, failures)
    self.assertEquals(cmd.parser.errors, errors)
    self.assertEquals(cmd.parser.skipped, skipped)
    self.assertIs(cmd.status, status)

class PyUnitTestCheckerTC(TestCase):
    input_dir = input_path('testcase_pkg/tests/')

    def setUp(self):
        self.checker = chks_python.PyUnitTestChecker(MockWriter())
        self.checker._coverage = None
        self.checker._path = input_path('')

    def input_path(self, path):
        return join(self.input_dir, path)

    def test_run_test_result_success(self):
        cmd = self.checker.run_test(self.input_path('unittest_success.py'))
        _test_cmd(self, cmd, SUCCESS, success=1)

    def test_run_test_result_failure(self):
        cmd = self.checker.run_test(self.input_path('unittest_failure.py'))
        _test_cmd(self, cmd, FAILURE, failures=1)

    def test_run_test_result_error(self):
        cmd = self.checker.run_test(self.input_path('unittest_errors.py'))
        _test_cmd(self, cmd, FAILURE, errors=1)

    def test_run_test_result_skipped(self):
        cmd = self.checker.run_test(self.input_path('unittest_skip.py'))
        _test_cmd(self, cmd, PARTIAL, skipped=1)

    def test_run_test_result_mixed(self):
        cmd = self.checker.run_test(self.input_path('unittest_mixed.py'))
        _test_cmd(self, cmd, ERROR, 2, 15, 1, 2)

    def test_run_test_result_mixed_std(self):
        cmd = self.checker.run_test(self.input_path('unittest_mixed_std.py'))
        _test_cmd(self, cmd, ERROR, 2, 15, 1, 0)


class PyTestCheckerTC(TestCase):
    input_dir = input_path('testcase_pkg/tests/')

    def setUp(self):
        self.checker = chks_python.PyTestChecker(MockWriter())
        self.checker._coverage = False

    def test(self):
        cwd = os.getcwd()
        os.chdir(input_path('testcase_pkg'))
        try:
            cmd = self.checker.run_test(['-c', 'from logilab.common.pytest import run; run()',],
                                        sys.executable)
            _test_cmd(self, cmd, ERROR, 5, 31, 3, 3)
        finally:
            os.chdir(cwd)

if __name__ == '__main__':
    unittest_main()
