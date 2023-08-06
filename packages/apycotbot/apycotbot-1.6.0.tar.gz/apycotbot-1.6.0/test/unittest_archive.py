import sys
import os
from os.path import join, exists
import tempfile

from logilab.common.testlib import TestCase, unittest_main, with_tempdir

from apycotbot.server import ApycotBotServer
from apycotbot.task import make_archive_name

class ApycotArchiveManagementTC(TestCase):

    def setUp(self):
        os.environ['APYCOTBOTRC'] = '/dev/null'
        self.bot = ApycotBotServer()
        # make a tmp_dir


    def _create_fake_archive(self, inst_id, exec_id, content="poulpe", dir_path=None):
        if dir_path is None:
            dir_path = self.bot['archive-dir']
        name = make_archive_name(inst_id, exec_id)
        arch_path = join(dir_path, name)
        arch = open(arch_path, 'w')
        arch.write(content)
        arch.close()
        return arch_path, (inst_id, exec_id)

    @with_tempdir
    def test_existing_archive(self):
        """Check that apycot bot propertly handle existing archive.

        You must be able to 

            * Retrieve the archive
            * multiple times
            * clean the archive
            """
        self.bot["archive-dir"] = tempfile.gettempdir()
        arch_a_path, arch_a_id = self._create_fake_archive('arch', 42, 'bob')
        arch_b_path, arch_b_id = self._create_fake_archive('arch', 18, 'tarzan')


        result_a_1 = self.bot.get_archive(*arch_a_id)
        self.assertEquals(result_a_1, 'bob')
        self.assertTrue(exists(arch_a_path))
        self.assertTrue(exists(arch_b_path))

        result_b_1 = self.bot.get_archive(*arch_b_id)
        self.assertEquals(result_b_1, 'tarzan')
        self.assertTrue(exists(arch_a_path))
        self.assertTrue(exists(arch_b_path))

        result_a_2 = self.bot.get_archive(*arch_a_id)
        self.assertEquals(result_a_2, 'bob')
        self.assertTrue(exists(arch_a_path))
        self.assertTrue(exists(arch_b_path))

        result_a_clean = self.bot.clear_archive(*arch_a_id)
        self.assertTrue(result_a_clean)
        self.assertFalse(exists(arch_a_path), "arch_a was not deleted")
        self.assertTrue(exists(arch_b_path))

        result_b_clean = self.bot.clear_archive(*arch_b_id)
        self.assertTrue(result_b_clean)
        self.assertFalse(exists(arch_a_path), "arch_a was not deleted")
        self.assertFalse(exists(arch_b_path))

    @with_tempdir
    def test_missing_archive(self):
        """Check that apycot bot propertly handle missing archive.

        Expected behaviour is :

            * You get nothing when you try to retrieve them.
            * You can not clean them. (as they don't exist).
            """
        exec_dir = self.bot["archive-dir"] = tempfile.gettempdir()
        arch_a_path, arch_a_id = self._create_fake_archive('coin', 1337, 'bob')
        imaginary_id = ('toto', 4562)

        result = self.bot.get_archive(*imaginary_id)
        self.assertNone(result)

        result_clean = self.bot.clear_archive(*imaginary_id)
        self.assertFalse(result_clean)



if __name__ == '__main__':
    unittest_main()
