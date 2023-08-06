"""unit tests for apycot.repositories"""

from logilab.common import testlib

import os
import pwd
import time
import tarfile
import tempfile
from copy import copy
from time import sleep
from shutil import rmtree
from os.path import exists, join
from datetime import datetime

from apycotbot.repositories import *
from logilab.devtools.vcslib.svn import CheckInInfo


from utils import input_path


class GetRepositoryTC(testlib.TestCase):
    def test(self):
        repo = get_repository({'repository': 'cvs:labas', 'path':'toto'})
        self.assert_(isinstance(repo, CVSRepository))
        repo_def = {'repository_type':'cvs', 'repository': 'labas', 'path':'toto'}
        repo = get_repository(repo_def)
        self.assert_(isinstance(repo, CVSRepository))
        self.assertEquals(repo_def, {})
        repo = get_repository({'repository_type': 'fs', 'repository':'toto'})
        self.assert_(isinstance(repo, FSRepository))



class CVSRepositoryTC(testlib.TestCase):
    _tested_class = CVSRepository
    name = 'cvs'


    def test_co_command(self):
        repo_def = {'repositoryy':'test', 'path': 'path'}
        self.assertRaises(ConfigError, self._tested_class, repo_def)
        repo_def = {'repository':'test', 'path': 'path'}
        repo = self._tested_class(repo_def)
        self.assertEquals(repo_def, {})
        self.assertEquals(repo.co_command(),
                          'cvs -d test -Q checkout -r HEAD path')
        repo_def = {'repository':'test', 'path': 'path', 'branch': 'branch'}
        repo = self._tested_class(repo_def)
        self.assertEquals(repo_def, {})
        self.assertEquals(repo.co_command(),
                          'cvs -d test -Q checkout -r branch path')

    def test_co_path(self):
        repo = self._tested_class({'repository':'test', 'path': 'toto/path'})
        self.assertEquals(repo.co_path(), 'path')

    def test_representative_attributes(self):
        repo = self._tested_class({'repository':'test', 'path': 'toto/path'})
        self.assertEquals(repo.representative_attributes(),
                          {'repository': 'test', 'path': 'toto/path',
                           'repository_type': self.name, 'branch': None})
        self.assertEquals(get_repository(repo.representative_attributes()),
                          repo)

    def test_specials(self):
        repo = self._tested_class({'repository':'test', 'path': 'toto/path'})
        self.assertEquals(repr(repo), '%s:test/toto/path' % self.name)
        self.assert_(repo == copy(repo))
        repo2 = self._tested_class({'repository':'test', 'path': 'tutu/path'})
        self.assert_(not repo == repo2)
        repo2 = FSRepository({'repository': 'toto/path'})
        self.assert_(not repo == repo2)

    def test_log_info(self):
        if os.system('cvs --help 2>/dev/null'):
            self.skip('vcs seems not installed')
        try:
            self.tmp1 = tempfile.mkdtemp(dir='/tmp')
            os.system('cvs -d %s init' % self.tmp1)
            os.mkdir(join(self.tmp1, 'module'))
            self.tmp2 = tempfile.mkdtemp(dir='/tmp')
            os.system(('cvs -d %s co -d %s module'
                      +' >/dev/null 2>/dev/null') % (self.tmp1, self.tmp2))
            f = os.path.join(self.tmp2, 'README')
            stream = file(f,'w')
            stream.write('hop')
            stream.close()
            os.system( ('(cd %s && cvs add README &&'
                       +' cvs ci -m "add readme file") >/dev/null 2>/dev/null')
                        % self.tmp2
                     )
            sleep(0.001) # added to avoid misterious missing ci
            stream = file(f,'w')
            stream.write('hop hop')
            stream.close()
            os.system(('(cd %s && cvs ci -m "update readme file")'
                      +' >/dev/null 2>/dev/null') % self.tmp2)
            #os.system('cd %s && cvs log' % self.tmp2)

            repo_path = self.tmp1
            if not exists(repo_path):
                self.skip('missing cvs repository %s'%repo_path)
            repo = self._tested_class({'repository': repo_path,
                                       'path': 'module'})

            user = pwd.getpwuid(os.getuid())[0]
            #user = os.getlogin()
            expected = [
                CheckInInfo(datetime(2008, 06, 11), user,
                                            u'update readme file', '1.2'),
                CheckInInfo(datetime(2008, 06, 11), user,
                                            u'add readme file', '1.1'),
                                            ]
            from_date = localtime(time.time() - 60*60*24)
            # add some minutes since it seems to be cvs log resolution
            to_date = localtime(time.time() + 1200)
            logs = list(repo.log_info(from_date, to_date))
            self.assertEquals(logs, expected)
            # support multiple date format
            logs = list(repo.log_info(time.mktime(from_date), to_date))
            self.assertListEquals(logs, expected)
            logs = list(repo.log_info(from_date, time.mktime(to_date)))
            self.assertListEquals(logs, expected)
        finally:
            # deletes temp files
            if exists(self.tmp1):
                rmtree(self.tmp1)
            if exists(self.tmp2):
                rmtree(self.tmp2)

class SVNRepositoryTC(CVSRepositoryTC):
    _tested_class = SVNRepository
    name = 'svn'

    def test_co_command(self):
        repo_def = {'repositoryy':'test', 'path': 'path'}
        self.assertRaises(ConfigError, SVNRepository, repo_def)
        repo_def = {'repository':'test', 'path': 'path'}
        repo = SVNRepository(repo_def)
        self.assertEquals(repo_def, {})
        self.assertEquals(repo.co_command(),
                          'svn checkout --non-interactive -q test/path')
        repo_def = {'repository':'test', 'path': 'path', 'branch': 'branch'}
        repo = SVNRepository(repo_def)
        self.assertEquals(repo_def, {})
        self.assertEquals(repo.co_command(),
                          'svn checkout --non-interactive -q test/branch')

    def test_co_path(self):
        repo = SVNRepository({'repository':'http://test.logilab.org/svn', 'path': 'toto/path'})
        self.assertEquals(repo.co_path(), 'path')

    def test_log_info(self):
        EXPECTED = (
        CheckInInfo(datetime(2008, 06, 10, 12, 42, 18), 'pyves',
            u'\n/\'\'\'\'\'\\\n \\   /\n  \\ /\n   o\n  /|\\\n  / \\', 'r9'),
        CheckInInfo(datetime(2008, 06, 10, 12, 41, 12), 'pyves',
            u'\nscramble scramble', 'r8'),
        CheckInInfo(datetime(2008, 06, 10, 12, 40, 46), 'pyves',
            u'\na plane', 'r7'),
        CheckInInfo(datetime(2008, 06, 10, 12, 39, 52), 'pyves',
            u'\ninitial files', 'r6'),
        # XXX don't expect this revision. svn bug? (using svn 1.5.6)
        CheckInInfo(datetime(2008, 06, 10, 11, 33, 29), 'pyves',
                    ur'/?\194?\176?\194?\176?\194?\176?\194?\176?\194?\176\ \ / \ / o /|\...',
            'r5'),
        )
        try:
            repo = tarfile.open(input_path("svn_test_repo.tar"))
            for tar_part in repo.getmembers():
                repo.extract(tar_part, input_path())
            repo_path = join(os.getcwd(), input_path('svn_test_repo'))
            repo = SVNRepository({'repository': 'file://%s' % repo_path,
                                  'path': ''})
            from_date = (2008, 6, 10, 11, 0, 0, 0, 0, 0)
            to_date = (2008, 6, 10, 12, 0, 0, 0, 0, 0)
            logs = list(repo.log_info(from_date, to_date))
            self.assertListEquals(logs, EXPECTED)
            # support multiple date format
            logs = list(repo.log_info(time.mktime(from_date), to_date))
            self.assertListEquals(logs, EXPECTED)

            logs = list(repo.log_info(from_date, time.mktime(to_date)))
            self.assertListEquals(logs, EXPECTED)
        finally:
            repo_path = input_path('svn_test_repo')
            if os.path.exists(repo_path):
                rmtree(repo_path)

class FSRepositoryTC(testlib.TestCase):

    def test_co_command(self):
        repo_def = {'pat': 'path'}
        self.assertRaises(ConfigError, FSRepository, repo_def)
        repo_def = {'repository': 'path'}
        repo = FSRepository(repo_def)
        self.assertEquals(repo_def, {})
        self.assertEquals(repo.co_command(), 'cp -R path .')

    def test_co_path(self):
        repo = FSRepository({'repository': 'toto/path'})
        self.assertEquals(repo.co_path(), 'path')

    def test_representative_attributes(self):
        repo = FSRepository({'repository': 'toto/path'})
        self.assertEquals(repo.representative_attributes(),
                          {'path': '', 'repository_type': 'fs', 'repository': 'toto/path', 'branch': None})
        self.assertEquals(get_repository(repo.representative_attributes()), repo)

    def test_specials(self):
        repo = FSRepository({'repository': 'toto/path'})
        self.assertEquals(repr(repo), 'fs:toto/path')
        self.assert_(repo == copy(repo))
        repo2 = FSRepository({'repository': 'tutu/path'})
        self.assert_(not repo == repo2)
        repo2 = CVSRepository({'repository':'test', 'path': 'toto/path'})
        self.assert_(not repo == repo2)

    def test_log_info(self):
        repo = FSRepository({'repository': 'toto/path'})
        self.assertRaises(NotSupported, repo.log_info, None, None)

class HGRepositoryTC(testlib.TestCase):
    def test_co_path(self):
        repo = HGRepository({'repository': 'toto/path', 'path': 'common'})
        self.assertEquals(repo.co_path(), 'path/common')
        repo = HGRepository({'repository': 'toto/path', 'path': 'common/sub'})
        self.assertEquals(repo.co_path(), 'path/common/sub')

if __name__ == '__main__':
    testlib.unittest_main()
