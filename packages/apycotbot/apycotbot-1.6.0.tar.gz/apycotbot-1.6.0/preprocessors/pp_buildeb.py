"""debian packages debian preprocessors

lgp command requires logilab's devtools package

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from os.path import abspath
from tempfile import mkdtemp

from apycotbot import register
from apycotbot.utils import Command
from apycotbot.preprocessors import BasePreProcessor


class LgpPreProcessor(BasePreProcessor):
    """preprocessor building debian package using lgp

       Use the devtools buildeb module to build debian packages. The upstream
       package should have a "debian" directory containing the debian packages
       description. The generated packages will be in the package upstream
       directory, allowing to call the lintian checker on them.
    """

    id = 'lgp_build'
    options_def = [{'name': 'distrib',
                    'help': "distribution(s) to build for. Default is set in '/etc/lgp/lgprc'",
                   },
                   {'name': 'archi',
                    'help': "architecture(s) to build for. Default is set in '/etc/lgp/lgprc'",
                   },
                   {'name': 'suffix',
                    'help': 'revision string appended to the Debian package name. '
                            'Prepend by ~ for pre-release and + for post-release',
                   },
                   {'name': 'verbose',
                    'help': 'set verbose mode',
                   },
                  ]

    # PreProcessor interface ##################################################

    def test_setup(self, test):
        """setup the test environment"""
        if hasattr(test, 'deb_packages_dir'):
            # already processed
            return
        # create a temp directory to put the generated files (deb, dsc...)
        test.deb_packages_dir = abspath(mkdtemp(dir='.'))
        cmd = ['lgp', 'build', '--result=%s' % test.deb_packages_dir,
               test.project_path()]
        if self.get_option('verbose', ''):
            cmd.append('--verbose')
        distrib = self.get_option('distrib', '')
        if distrib:
            cmd.append('--distrib=%s' % distrib)
        archi = self.get_option('archi', '')
        if archi:
            cmd.append('--arch=%s' % archi)
        suffix = self.get_option('suffix', "")
        if suffix:
            suffix += test.apycot_repository().revision()
            cmd.append('--suffix=%s' % suffix)
        cmd = Command(self.writer, cmd, raises=True)
        cmd.run()

register('preprocessor', LgpPreProcessor)
