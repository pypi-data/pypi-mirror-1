"""Checkers for global package structure


:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import os
from os.path import exists, join
from commands import getoutput

from logilab.common.textutils import splitstrip

from apycotbot import register
from apycotbot.utils import SUCCESS, NODATA, FAILURE, ParsedCommand
from apycotbot.checkers import BaseChecker, AbstractFilteredFileChecker
from apycotbot.checkers.chks_rest import ReSTChecker, docutils_version
from apycotbot.checkers.chks_xml import XmlFormChecker
from apycotbot.checkers.chks_html import HTMLChecker, HAS_TIDY

REQUIRED_FILES = ['README']
RECOMMANDED_FILES = ['ChangeLog', 'INSTALL']

class PackageDocChecker(BaseChecker):
    """check some standard package documentation :

       * presence of some required files (README, INSTALL, ChangeLog)
       * plain text files in the "doc" directory are ReST files
       * xml files in the "doc" directory are well formed
       * html files in the "doc" directory are correct

       The 3 last tests will be done according to the presence of the respective
       checkers (which depends on external packages).
    """
    need_preprocessor = 'build_doc'
    id = 'pkg_doc'
    options_def = AbstractFilteredFileChecker.options_def

    def __init__(self, writer, options=None):
        BaseChecker.__init__(self, writer, options)
        self._checkers = []
        self._checkers.append(XmlFormChecker(self.writer))
        if docutils_version is not None:
            self._rest_checker = ReSTChecker(self.writer)
            self._checkers.append(self._rest_checker)
        else:
            self._rest_checker = None
        if HAS_TIDY:
            self._checkers.append(HTMLChecker(self.writer))

    def _run(self, test):
        """run the checker against <path> (usually a directory)"""
        status = SUCCESS
        path = test.project_path()
        ignore = self.get_option('ignore', '')
        for checker in self._checkers:
            checker.version_info()
            checker.options['ignore'] = ignore
        if exists(join(path, 'doc')):
            for checker in self._checkers:
                _res = checker.run(test)
                if _res != NODATA:
                    status = self.merge_status(status, _res)
        if self._rest_checker is None:
            return status
        for filename in REQUIRED_FILES + RECOMMANDED_FILES:
            filename = join(path, filename)
            if exists(filename):
                _res =  self._rest_checker.check_file(filename)
                status = self.merge_status(status, _res)
        return status

register('checker', PackageDocChecker)


class LgpCheckChecker(BaseChecker):
    """check debian packages by lgp check command

    Check a package is conform to the `standard source tree` as described in the
    devtools package for a Python package. It'll also check the content of some 
    of the specified files, like __pkginfo__.py, MANIFEST.in...

    You can set lgp specific checks with configuration variable lgp_check_set
    You can include lgp specific checks with configuration variable lgp_check_include
    You can exclude lgp specific checks with configuration variable lgp_check_exclude

    """
    id = 'lgp_check'
    need_preprocessor = None
    options_def = [
        {'name': 'set', 'type': 'csv',
         'help': 'comma separated list of lgp checks to run',
         },
        {'name': 'include', 'type': 'csv',
         'help': 'comma separated list of lgp checks to include',
         },
        {'name': 'exclude', 'type': 'csv',
         'help': 'comma separated list of lgp checks to exclude',
         },
        ]

    def __init__(self, writer, options=None):
        BaseChecker.__init__(self, writer, options)
        self.set_lgp_checks = splitstrip(self.get_option('set', ''))
        self.include_lgp_checks = splitstrip(self.get_option('include', ''))
        self.exclude_lgp_checks = splitstrip(self.get_option('exclude', ''))

    def run(self, test):
        path = test.project_path()
        cmdline = ['lgp', 'check', path]
        if self.set_lgp_checks:
            cmdline += ['-s', ','.join(self.set_lgp_checks)]
        if self.include_lgp_checks:
            cmdline += ['-i', ','.join(self.include_lgp_checks)]
        if self.exclude_lgp_checks:
            cmdline += ['-e', ','.join(self.exclude_lgp_checks)]
        # unset python path, we want to use installed library
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        cmd = ParsedCommand(self.writer, cmdline)
        cmd.non_zero_status_code = FAILURE
        return cmd.run()

    def version_info(self):
        self.record_version_info('lgp', getoutput("lgp --version").strip())

register('checker', LgpCheckChecker)
