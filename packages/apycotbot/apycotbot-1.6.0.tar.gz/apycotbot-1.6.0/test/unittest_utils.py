"""unit tests for the apycotbot.utils module"""
import sys, os
from logilab.common.testlib import TestCase, unittest_main

from apycotbot.utils import EnvironmentTrackerMixin

class EnvironmentTrackerMixinTC(TestCase):

    def setUp(self):
        os.environ['PYTHONPATH'] = ''
        self.tracker = EnvironmentTrackerMixin()

    def test_update_clean_env(self):
        lc_all = os.environ.get('LC_ALL')
        self.tracker.update_env('key', 'LC_ALL', 'XXXX')
        self.assertEquals(os.environ['LC_ALL'], 'XXXX')
        self.tracker.clean_env('key', 'LC_ALL')
        self.assertEquals(os.environ.get('LC_ALL'), lc_all)

        self.tracker.update_env('key', '__ENVIRONMENTTRACKERMIXINTC__', 'XXXX')
        self.assertEquals(os.environ['__ENVIRONMENTTRACKERMIXINTC__'], 'XXXX')
        self.tracker.clean_env('key', '__ENVIRONMENTTRACKERMIXINTC__')
        self.assertRaises(KeyError, os.environ.__getitem__,
                          '__ENVIRONMENTTRACKERMIXINTC__')

    def test_nested(self):
        lc_all = os.environ.get('LC_ALL')
        self.tracker.update_env('key', 'LC_ALL', 'XXXX')
        self.assertEquals(os.environ['LC_ALL'], 'XXXX')
        self.tracker.update_env('key2', 'LC_ALL', 'YYYY')
        self.assertEquals(os.environ['LC_ALL'], 'YYYY')
        self.tracker.clean_env('key2', 'LC_ALL')
        self.assertEquals(os.environ['LC_ALL'], 'XXXX')
        self.tracker.clean_env('key', 'LC_ALL')
        self.assertEquals(os.environ.get('LC_ALL'), lc_all)

    def test_update_clean_env_sep(self):
        path = os.environ['PATH']
        self.tracker.update_env('key', 'PATH', '/mybin', ':')
        self.assertEquals(os.environ['PATH'], '/mybin:' + path)
        self.tracker.clean_env('key', 'PATH')
        self.assertEquals(os.environ['PATH'], path)

    def test_nested_sep(self):
        path = os.environ['PATH']
        self.tracker.update_env('key', 'PATH', '/mybin', ':')
        if path:
            self.assertEquals(os.environ['PATH'], '/mybin:' + path)
        else:
            self.assertEquals(os.environ['PATH'], '/mybin')
        self.tracker.update_env('key2', 'PATH', '/myotherbin', ':')
        if path:
            self.assertEquals(os.environ['PATH'], '/myotherbin:/mybin:' + path)
        else:
            self.assertEquals(os.environ['PATH'], '/myotherbin:/mybin')
        self.tracker.clean_env('key2', 'PATH')
        if path:
            self.assertEquals(os.environ['PATH'], '/mybin:' + path)
        else:
            self.assertEquals(os.environ['PATH'], '/mybin')
        self.tracker.clean_env('key', 'PATH')
        self.assertEquals(os.environ['PATH'], path)

    def test_python_path_sync(self):
        self.tracker.update_env('key', 'PYTHONPATH', '/mylib', ':')
        self.assertEquals(os.environ['PYTHONPATH'], '/mylib')
        self.assertEquals(sys.path[0], '/mylib')
        self.tracker.update_env('key2', 'PYTHONPATH', '/otherlib', ':')
        self.assertEquals(os.environ['PYTHONPATH'], '/otherlib:/mylib')
        self.assertEquals(sys.path[0], '/otherlib')
        self.tracker.clean_env('key2', 'PYTHONPATH')
        self.assertEquals(os.environ['PYTHONPATH'], '/mylib')
        self.assertNotEquals(sys.path[0], '/otherlib')
        self.tracker.clean_env('key', 'PYTHONPATH')
        self.assertEquals(os.environ['PYTHONPATH'], '')
        self.assertNotEquals(sys.path[0], '/otherlib')

    def test_update_undefined_env(self):

        var = 'XNZOUACONFVESUHFJGSLKJ'
        while os.environ.get(var) is not None:
            var = ''.join(chr(randint(ord('A'), ord('Z') +1))
                for cnt in xrange(randint(10, 20)))

        self.tracker.update_env('key', var, 'to be or not to be', ':')
        self.assertTextEquals(os.environ.get(var),  'to be or not to be')
        self.tracker.clean_env('key', var)
        self.assertEquals(os.environ.get(var), None)


if __name__ == '__main__':
    unittest_main()
