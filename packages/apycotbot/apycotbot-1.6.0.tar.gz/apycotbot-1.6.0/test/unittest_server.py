import sys, datetime

from logilab.common.testlib import TestCase, unittest_main, mock_object

from apycotbot.server import ApycotBotServer
from apycotbot.utils import ConnectionHandler
from apycotbot.task import ApycotTask, extract_test_config

def fake_test_config(self, envname, tcname):
    return mock_object(metainformation=lambda x: {'source':{'uri': 'system'}},
                       name='bob', eid=0,
                       all_checks=['pyunit'],
                       environment=mock_object(name='lgc')
                       )
ConnectionHandler.test_config = fake_test_config

ConnectionHandler.connect = lambda x: None

def fake_start_task(self, task):
    task.starttime = datetime.datetime.now()
    self._running_tasks.add(task)
ApycotBotServer._start_task = fake_start_task

class ApycotBotServerTC(TestCase):
    orig_argv = sys.argv
    def setUp(self):
        self.bot = ApycotBotServer()

    def tearDown(self):
        sys.argv = self.orig_argv

    def test_same_test_short_interval(self):
        self.bot.queue_task('pop', 'pouet')
        self.assertEquals(self.bot._queue.qsize(), 1)
        self.bot._start_tasks()
        self.assertEquals(self.bot._queue.qsize(), 0)
        self.bot.queue_task('pop', 'pouet')
        self.assertEquals(self.bot._queue.qsize(), 0)

    def test_same_test_but_diff_checks_short_interval(self):
        self.bot.queue_task('pop', 'pouet')
        self.assertEquals(self.bot._queue.qsize(), 1)
        self.bot._start_tasks()
        self.assertEquals(self.bot._queue.qsize(), 0)
        self.bot.queue_task('pop', 'pouet', branch='stable')
        self.assertEquals(self.bot._queue.qsize(), 1)

    consider_only = set(('dpkg-deb', 'lgp_check', 'pkg_doc', 'pychecker', 'rest_syntax',
                         'xml_valid'))
    def test_available_checkers(self):
        self.assertListEquals(
            [d for d in self.bot.available_checkers()
             if d['id'] in self.consider_only],
            [{'id': 'dpkg-deb', 'preprocessor': 'debian',
              'help': 'debian package archive manipulation tool'},
             {'id': 'lgp_check', 'preprocessor': None,
              'help': 'check debian packages by lgp check command'},
             {'id': 'pkg_doc', 'preprocessor': 'build_doc',
              'help': 'check some standard package documentation :'},
             {'id': 'pychecker', 'preprocessor': 'install',
              'help': 'check that unit tests of a python package succeed'},
             {'id': 'rest_syntax', 'preprocessor': None,
              'help': 'check syntax of ReST file'},
             {'id': 'xml_valid', 'preprocessor': None,
              'help': 'check validity of xml file'},
             ])

    def test_available_preprocessors(self):
        self.assertListEquals(
            self.bot.available_preprocessors(),
            [{'id': 'lgp_build',
              'help': 'preprocessor building debian package using lgp'},
             {'id': 'make',
              'help': 'make preprocessor'},
             # {'id': 'python_setenv',
             #  'help': 'a preprocessor to setup a test correctly when the pp_setup'},
             {'id': 'python_setup',
              'help': 'python setup.py pre-processor'},
             {'id': 'zope_install',
              'help': 'install a product in a zope test environment (INSTANCE_HOME)'}])

    def test_available_options(self):
        self.assertListEquals(
            clean_options(
                [d for d in self.bot.available_options()
                 if d.get('checker') is None
                 or d['checker'] in self.consider_only]),
            [{'name': 'plugins', 'help': 'comma sepa'},
             {'name': 'test-dir', 'help': 'directory '},
             {'name': 'archive-dir', 'help': 'directory '},
             {'name': 'max-cpu-time', 'help': 'maximum CP'},
             {'name': 'max-time', 'help': 'maximum Re'},
             {'name': 'max-memory', 'help': 'maximum Me'},
             {'name': 'max-reprieve', 'help': 'delay in s'},
             {'checker': 'dpkg-deb', 'name': 'ignore', 'help': 'comma sepa'},
             {'checker': 'lgp_check', 'name': 'set', 'help': 'comma sepa'},
             {'checker': 'lgp_check', 'name': 'include', 'help': 'comma sepa'},
             {'checker': 'lgp_check', 'name': 'exclude', 'help': 'comma sepa'},
             {'checker': 'pkg_doc', 'name': 'ignore', 'help': 'comma sepa'},
             {'checker': 'rest_syntax', 'name': 'ignore', 'help': 'comma sepa'},
             {'checker': 'xml_valid', 'name': 'ignore', 'help': 'comma sepa'},
             {'preprocessor': 'lgp_build', 'name': 'distrib', 'help': 'distributi'},
             {'preprocessor': 'lgp_build', 'name': 'archi', 'help': 'architectu'},
             {'preprocessor': 'lgp_build', 'name': 'suffix', 'help': 'revision s'},
             {'help': 'set verbos', 'preprocessor': 'lgp_build', 'name': 'verbose'},
             {'preprocessor': 'make', 'name': 'make', 'help': 'make comma'},
             {'preprocessor': 'make', 'name': 'makefile', 'help': 'make file '},
             {'preprocessor': 'make', 'name': 'target', 'help': 'make speci'},
             {'preprocessor': 'make', 'name': 'directories', 'help': 'Comma sepa'}])

def clean_options(dictlist):
    for optdict in dictlist:
        if 'required' in optdict and not optdict['required']:
            del optdict['required']
        del optdict['type']
        optdict.pop('id', None)
        optdict['help'] = optdict['help'][:10]
    return dictlist

if __name__ == '__main__':
    unittest_main()
