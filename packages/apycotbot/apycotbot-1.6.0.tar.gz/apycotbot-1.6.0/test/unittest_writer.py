"""unit tests for the apycotbot.writer module"""
import os
from logilab.common.testlib import TestCase, unittest_main

from apycotbot.writer import DataWriter
        
class DataWriterTC(TestCase):
    
    def setUp(self):
        self.writer = DataWriter(None, 1)

    def test__msg_info_01(self):
        path, line, msg = self.writer._msg_info('bonjour %s', 'vous')
        self.assertEquals(path, None)
        self.assertEquals(line, None)
        self.assertEquals(msg, 'bonjour vous')

    def test__msg_info_02(self):
        path, line, msg = self.writer._msg_info('bonjour %s', 'vous', path='/tmp', line=1)
        self.assertEquals(path, '/tmp')
        self.assertEquals(line, 1)
        self.assertEquals(msg, 'bonjour vous')

    def test__msg_info_03(self):
        try:
            os.path.isdir(1)
        except:
            path, line, msg = self.writer._msg_info('oops %s', 'badaboum', tb=True)
        self.assertEquals(path, None)
        self.assertEquals(line, None)
        self.failUnless(msg.startswith('oops badaboum'))
        self.failUnless('Traceback' in msg)


if __name__ == '__main__':
    unittest_main()
