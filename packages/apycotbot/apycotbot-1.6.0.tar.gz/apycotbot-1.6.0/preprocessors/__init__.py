"""preprocessors register

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from apycotbot import SetupException
from apycotbot.utils import ApycotObject


class BasePreProcessor(ApycotObject):
    """an abstract class providing some common utilities for preprocessors
    """
    __type__ = 'preprocessor'

    # PreProcessor interface ##################################################

    def test_setup(self, test):
        """setup the test environment"""
        raise NotImplementedError()

    def dependency_setup(self, test, path):
        """setup the test environment"""
        raise SetupException('this preprocessor doesn\'t handle dependencies')

# import submodules
import apycotbot.preprocessors.pp_setup
import apycotbot.preprocessors.pp_make
import apycotbot.preprocessors.pp_zope_install
import apycotbot.preprocessors.pp_buildeb
