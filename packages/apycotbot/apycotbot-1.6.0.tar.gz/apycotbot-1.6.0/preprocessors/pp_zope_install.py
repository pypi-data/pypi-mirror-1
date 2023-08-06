"""installation preprocessor for Zope products

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"


import os
from os.path import join, abspath, basename

from apycotbot import register
from apycotbot.preprocessors import BasePreProcessor
from apycotbot.utils import EnvironmentTrackerMixin

class ZopeInstanceProcessor(EnvironmentTrackerMixin, BasePreProcessor):
    """install a product in a zope test environment (INSTANCE_HOME)

       Install a Zope product in a Zope test environment (i.e. INSTANCE_HOME),
       by creating a symbolic link of the extracted directory in the instance's
       Products directory. The user running tester must be able to create this
       link !
    """

    id = 'zope_install'

    def __init__(self, writer, options):
        EnvironmentTrackerMixin.__init__(self)
        BasePreProcessor.__init__(self, writer, options)
        self._installed = {}

    # PreProcessor interface ##################################################

    def test_setup(self, test):
        """setup the test environment"""
        self._install(test.repo.path)

    def dependency_setup(self, test, path):
        """setup the test environment

        may raise a SetupException
        """
        self._install(path)

    # private #################################################################

    def _install(self, path):
        """run the distutils setup.py install method on a path if
        the path is not yet installed
        """
        products_dir = join(os.environ.get('INSTANCE_HOME',
                                           '/var/lib/zope/instance/test'),
                            'Products')
        self._installed[path] =  join(products_dir, basename(path))
        try:
            os.symlink(abspath(path), self._installed[path])
        except OSError, ex:
            ex.args += (abspath(path), self._installed[path])
            raise

    def _uninstall(self, path):
        """run the distutils setup.py install method on a path if
        the path is not yet installed
        """
        os.remove(self._installed[path])
        del self._installed[path]

register('preprocessor', ZopeInstanceProcessor)
