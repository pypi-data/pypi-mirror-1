"""subpackage containing base checkers (mostly for python code and packaging
standard used at Logilab)

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from os.path import walk, splitext, split, join

from logilab.common.textutils import splitstrip

from apycotbot.utils import SUCCESS, MISSING, NODATA, TestStatus, ApycotObject

class BaseChecker(ApycotObject):
    __type__ = 'checker'
    need_preprocessor = None

    _best_status = None

    def run(self, test):
        status = self._run(test)
        new_status = self.merge_status(status, self.best_status)
        self.version_info()
        if new_status is status:
            return status
        self.writer.info(None, None,
                        "Configuration's setting downgrade %s checker status '\
                        'from <%s> to <%s>" % (self.id, status, new_status))
        return new_status

    def ignore_option(self):
        """used by AbstractFilteredFileChecker and pylint checker at least"""
        ignored = set(('CVS', '.svn', '.hg'))
        for string in splitstrip(self.get_option('ignore', '')):
            ignored.add(string)
        return ignored

    def _get_best_status(self):
        best_status = self._best_status
        if best_status is None:
            return None
        if not isinstance(best_status, TestStatus):
            best_status = TestStatus.get(best_status)
        return best_status

    def _set_best_status(self, value):
        if not isinstance(value, TestStatus):
            value = TestStatus.get(value)
        self._best_status = value

    best_status = property(_get_best_status, _set_best_status)

    def version_info(self):
        """hook for checkers to add their version information"""

    def _run(self, test):
        raise NotImplementedError()


class MissingChecker(BaseChecker):
    options_def = {}

    def __init__(self, writer, name, msg=None):
        self.id = name
        self.writer = writer
        self.msg = msg or 'no such checker %s' % name
        self.options = {}

    def _run(self, test):
        self.writer.fatal(self.msg)
        return MISSING


class AbstractFilteredFileChecker(BaseChecker):
    """check a directory file by file, with an extension filter
    """
    checked_extensions =  None
    options_def = [{'name': 'ignore', 'type': 'csv',
                    'help': 'comma separated list of files or directories to ignore',
                   },
                  ]
    def __init__(self, writer, options=None, extensions=None):
        BaseChecker.__init__(self, writer, options)
        self.extensions = extensions or self.checked_extensions
        if isinstance(self.extensions, basestring):
            self.extensions = (self.extensions,)
        self._res = None
        self._safe_dir = set()

    def files_root(self, test):
        return test.project_path(subpath=True)

    def _run(self, test):
        """run the checker against <path> (usually a directory)

        return true if the test succeeded, else false.
        """
        self._res = SUCCESS
        self._nbanalyzed = 0
        ignored = self.ignore_option()
        def walk_handler(arg, directory, fnames):
            """walk callback handler"""
            for file in ignored: # fnamesneed to be replace in place
                if file in fnames:
                    fnames.remove(file)
            for filename in fnames:
                ext = splitext(filename)[1]
                if self.extensions is None or ext in self.extensions:
                    res = self.check_file(join(directory, filename))
                    self._res = self.merge_status(self._res, res)
                    self._nbanalyzed += 1
        walk(self.files_root(test), walk_handler, None)
        self.writer.raw('total files analyzed', self._nbanalyzed)
        if self._nbanalyzed <= 0:
            self._res = self.merge_status(self._res, NODATA)
        return self._res


# import submodules
#
#  chks_pt should not be imported explicitly, because it takes a long time to
#  import all the related Zope machinery
import apycotbot.checkers.chks_debian
import apycotbot.checkers.chks_pkg
import apycotbot.checkers.chks_python
import apycotbot.checkers.chks_rest
import apycotbot.checkers.chks_xml
import apycotbot.checkers.chks_html
import apycotbot.checkers.chks_pt
