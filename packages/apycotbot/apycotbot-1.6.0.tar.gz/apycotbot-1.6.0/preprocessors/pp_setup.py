"""installation preprocessor using distutils setup.py

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"


import os
import shutil
from os.path import join, exists, abspath

from apycotbot import register, SetupException
from apycotbot.utils import EnvironmentTrackerMixin, Command
from apycotbot.preprocessors import BasePreProcessor


class DistutilsProcessor(EnvironmentTrackerMixin, BasePreProcessor):#SetPythonEnvProcessor):
    """python setup.py pre-processor

       Use a distutils'setup.py script to install a Python package. The
       setup.py should provide an "install" function which run the setup and
       return a "dist" object (i.e. the object return by the distutils.setup
       function). This preprocessor may modify the PATH and PYTHONPATH
       environment variables.
    """
    id = 'python_setup'
    _python_path_set = None
    _installed = set()

    def __init__(self, writer, options):
        EnvironmentTrackerMixin.__init__(self)
        BasePreProcessor.__init__(self, writer, options)

    def set_env(self, test):
        if not DistutilsProcessor._python_path_set:
            path = test.project_path()
            py_lib_dir = join(os.getcwd(), 'local', 'lib', 'python')
            # setuptools need this directory to exists
            if not exists(py_lib_dir):
                os.makedirs(py_lib_dir)
            self.update_env(path, 'PYTHONPATH', py_lib_dir, os.pathsep)
            DistutilsProcessor._python_path_set = py_lib_dir
            bin_dir = join(os.getcwd(), 'bin')
            self.update_env(path, 'PATH', bin_dir, os.pathsep)
        return DistutilsProcessor._python_path_set

    # PreProcessor interface ##################################################

    def test_setup(self, test):
        """setup the test environment"""
        # must be done  before _install in case setuptools is used
        self.set_env(test)
        self._install(test, test.project_path())

    def dependency_setup(self, test, path):
        """setup the test environment

        may raise a SetupException
        """
        # must be done  before _install in case setuptools is used
        self.set_env(test)
        self._install(test, path)

    # private #################################################################

    def _install(self, test, path):
        """run the distutils setup.py install method on a path if
        the path is not yet installed
        """
        # cache to avoid multiple installation of the same module
        if path in self._installed:
            return
        if not exists(join(path, 'setup.py')):
            raise SetupException('No file %s' % abspath(join(path, 'setup.py')))
        self._installed.add(path)
        # FIXME keep compatibility with python2.4 in Debian stable (etch)
        # FIXME Feel free to use the 'with' statement afterwards.
        #with pushd(path):
        cwd = os.getcwd()
        os.chdir(path)
        try:
            cmd = Command(self.writer,
                          ['python', 'setup.py', 'install', '--home',
                           join(test.tmpdir, 'local'), '--quiet'], raises=True)
            cmd.run()
            if exists('build'):
                shutil.rmtree('build') # remove the build directory
        finally:
            os.chdir(cwd)


register('preprocessor', DistutilsProcessor)
