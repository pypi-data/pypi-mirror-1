"""checkers for debian packages, using lintian and/or piuparts

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import os
import os.path
from commands import getoutput

from logilab.common.textutils import splitstrip

from apycotbot import register
from apycotbot.checkers import AbstractFilteredFileChecker
from apycotbot.utils import SUCCESS, FAILURE, ERROR, Command, ParsedCommand, SimpleOutputParser

class DebianChecker(AbstractFilteredFileChecker):
    need_preprocessor = 'debian'

    def files_root(self, test):
        return test.deb_packages_dir


class DebianLintianChecker(DebianChecker):
    """check debian changes files by parsing lintian output"""
    id = 'lintian'
    checked_extensions = ('.changes',)

    def check_file(self, filepath):
        cmdline = ['lintian', '-v', filepath]
        return ParsedCommand(self.writer, cmdline).run()

    def version_info(self):
        self.record_version_info('lintian', getoutput("lintian -V").strip())

register('checker', DebianLintianChecker)


class DebianDebLintianChecker(DebianLintianChecker):
    """check debian packages by parsing lintian output"""
    id = 'lintian_deb'
    checked_extensions = ('.deb',)

register('checker', DebianDebLintianChecker)


class DebianPiupartsChecker(DebianChecker):
    """check debian packages by parsing piuparts output"""
    id = 'piuparts'
    checked_extensions = ('.changes')
    options_def = (
                  #{'name': 'ignore_regexp', 'type': 'csv',
                  # 'help': ('comma separated list of regular expression that will '
                  # 'be given to piuparts using its -I option.'),
                  #},
                  )

    def check_file(self, filepath):
        #self.ignore_regexp = splitstrip(self.get_option('ignore_regexp'))

        cmdline = ['lgp', 'piuparts', '--verbose']
        #for line in self.ignore_regexp:
        #    cmdline.append("-I")
        #    cmdline.append(line)
        cmdline.append(filepath)

        return ParsedCommand(self.writer, cmdline).run()

    def version_info(self):
        self.record_version_info('piuparts',
                                 getoutput("piuparts --version").strip())

register('checker', DebianPiupartsChecker)


class DpkgDebChecker(DebianChecker):
    """debian package archive manipulation tool"""
    id = 'dpkg-deb'
    checked_extensions = ('.deb',)

    def check_file(self, filepath):
        return Command(self.writer, ['dpkg-deb', '-I', filepath]).run()

    def version_info(self):
        self.record_version_info('dpkg-deb',
                                 getoutput("dpkg-deb --version").strip())

register('checker', DpkgDebChecker)


class LdiOutputParser(SimpleOutputParser):
    def map_message(self, mtype, msg):
        if mtype == 'WARN':
            self.writer.warning(msg, path=self.path)
        elif 'ERROR' in mtype:
            self.writer.error(msg, path=self.path)
            status = FAILURE
        elif 'CRITICAL' in mtype:
            self.writer.fatal(msg, path=self.path)
            status = FAILURE
        elif msg:
            self.unparsed.append(msg)


class LdiUploadChecker(DebianChecker):
    """upload debian packages by ldi command

    We re-test the 'lgp_check' and 'lintian' checkers internally to allow
    the debian package upload if use_chain configuration variable is set to True

    Configuration:
    - you need to define the 'ldi_upload_repository' variable to a valid repository
    - it's possible to override the /etc/debinstall/debinstallrc file by the
      'ldi_upload_debinstallrc' variable
    """
    id = 'ldi_upload'
    checked_extensions = ('.changes',)
    options_def = [{'name': 'repository', 'required': True,
                'help': 'ldi repository name',
                },
               {'name': 'debinstallrc',
                'help': ('debinstall configuration file. '
                         '/etc/debinstall/debinstallrc by default.'),
                },
               {'name': 'require_checks',
                'help': ('Comma separated list of debinstall checks to run '
                         'before upload. lintian by default.'),
                }
               ]


    def __init__(self, writer, options=None):
        DebianChecker.__init__(self, writer, options)
        self.repository = self.get_option('repository')
        self.debinstallrc = self.get_option('debinstallrc', '/etc/debinstall/debinstallrc')
        self.require_checks = splitstrip(self.get_option('require_checks',
                                                      'lintian'))

    def version_info(self):
        self.record_version_info('ldi', getoutput("ldi --version").strip())

    def run(self, test):
        """run the checker against <path> (usually a directory)

        return true if the test succeeded, else false.
        """
        for checker in self.require_checks:
            if not checker in test.executed_checkers:
                self.writer.error("%s checker has not been executed",
                                  checker, path=test.project_path())
                return ERROR
            if not test.executed_checkers[checker] == SUCCESS:
                self.writer.error("%s checker has not succeed",
                                  checker, path=test.project_path())
                return ERROR

        # FIXME https://www.logilab.net/elo/ticket/7967
        os.system('chmod a+rx -R %s ' % os.path.dirname(self.files_root(test)))
        return super(LdiUploadChecker, self)._run(test)

    def check_file(self, filepath):
        command = ['ldi', 'upload', '-c', self.debinstallrc, self.repository, filepath]
        return ParsedCommand(self.writer, command, parsercls=LdiOutputParser).run()

register('checker', LdiUploadChecker)
