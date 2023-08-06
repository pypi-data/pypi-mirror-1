from logilab.common.testlib import mock_object
from os.path import join, dirname, abspath

INPUTS_DIR = abspath(join(dirname(__file__), 'data'))

def input_path(file=''):
    return join(INPUTS_DIR, file)

from apycotbot.writer import DataWriter

class MockWriter(DataWriter):
    """fake apycot.IWriter class, ignore every thing"""

    def skip(self, *args, **kwargs):
        pass
    def _debug(self, *args, **kwargs):
        print args, kwargs
    __init__= skip
    raw = log = execution_info = skip
    start_test = start_check = end_check = end_test = skip
    set_exec_status = skip

class MockTest:
    """fake apycot.Test.Test class"""
    def __init__(self, repo=None):
        self.repo = repo
        self.tmpdir = 'data'
        self.environ = {}
        self.checkers = []

    def project_path(self, subpath=False):
        return self.repo.co_path()

    @property
    def tconfig(self):
        return mock_object(testconfig={}, name='bob', subpath=None)

    def apycot_config(self, something=None):
        return {}

class MockRepository:
    """fake apycot.IRepository class"""
    branch = None
    def __init__(self, attrs=None, **kwargs):
        self.__dict__.update(kwargs)

    def co_command(self):
        return self.command

    def co_path(self):
        return self.path

    def co_move_to_branch_command(self):
        return None

    def representative_attributes(self):
        return {}

    def log_info(self, from_date, to_date):
        """get list of log messages

        a log information is a tuple
        (file, revision_info_as_string, added_lines, removed_lines)
        """
        yield CheckInInfo(datetime.fromtimestamp(time()), 'author',
            u"log message", 'r1234', 6, 3, files=('xxx/file', ))

    def __repr__(self):
        return '<MockRepository %r>' % self.__dict__

    def revision(self):
        pass


class MockConnection(object):
    """fake pyro connexion"""
    def close(self):
        pass
