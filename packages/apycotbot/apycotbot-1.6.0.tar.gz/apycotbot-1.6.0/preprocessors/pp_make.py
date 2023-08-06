"""installation / build preprocessor using make

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"


import os
from os.path import abspath, join

from logilab.common.textutils import splitstrip

from apycotbot import register
from apycotbot.utils import Command
from apycotbot.preprocessors import BasePreProcessor

class MakeProcessor(BasePreProcessor):
    """make preprocessor

       A whatever builder / installer using make. You can configure this
       preprocessor to run make in the desired package subdirectories (if no
       one provided, make will be run at the root of the package).
    """
    id = 'make'
    options_def = [{'name': 'make',
                    'help': 'make command. Default to "make".',
                    },
                   {'name': 'makefile',
                    'help': ('make file to be used. Default to "makefile"'),
                    },
                   {'name': 'target',
                    'help': ('make specific target. No target given to make by '
                             'default.'),
                    },
                   {'name': 'directories',
                    'help': ('Comma separated list of directories where make '
                             'should be executed. By default, executed into the '
                             'checkout directory.'),
                    },
                   ]

    binpath = 'make'
    _installed = {}

    def __init__(self, writer, options):
        BasePreProcessor.__init__(self, writer, options)

    def make_command(self):
        command = [self.get_option('make', self.binpath)]
        makefile = self.get_option('makefile', None)
        if makefile:
            command.append('-f')
            command.append(makefile)
        target = self.get_option('target', None)
        if target:
            command.append(target)
        return Command(self.writer, command)

    def make_setup(self, path):
        """setup the test environment"""
        # cache to avoid multiple installation of the same module
        if self._installed.has_key(path):
            return self._installed[path]
        command = self.make_command()
        self._run(command, path)

    def _run(self, command, basepath):
        """execute <command> in each directory"""
        directories = splitstrip(self.get_option('directories')) or (basepath,)
        # FIXME keep compatibility with python2.4 in Debian stable (etch)
        # FIXME Feel free to use the 'with' statement afterwards.
        #with pushd(abspath(basepath)) as basepath:
        cwd = os.getcwd()
        basepath = abspath(basepath)
        os.chdir(basepath)
        try:
            for directory in directories:
                try:
                    os.chdir(directory)
                except OSError, ex:
                    self.writer.error(str(ex), path=join(basepath, directory))
                    continue
                command.run()
                os.chdir(basepath)
        finally:
            os.chdir(cwd)

    # PreProcessor interface ##################################################

    def test_setup(self, test):
        """setup the test environment"""
        self.make_setup(test.project_path())

    def dependency_setup(self, test, path):
        """setup the test environment"""
        self.make_setup(path)


register('preprocessor', MakeProcessor)
