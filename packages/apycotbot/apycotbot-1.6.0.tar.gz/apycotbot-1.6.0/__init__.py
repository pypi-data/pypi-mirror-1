# Copyright (c) 2003-2009 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""APyCoT, A Pythonic Code Tester

this is the bot part of the code tester, responsible to execute checks
"""

from os.path import exists, join, dirname
MODE = exists(join(dirname(__file__), '.hg')) and 'dev' or 'installed'

class Registry(dict):
    """a registry is a two level dictionnary to group together object in a
    same class
    """

    def get(self, category, name):
        """get a object by name"""
        try:
            return self[category][name]
        except KeyError:
            raise ConfigError('No object %r in category %r' % (name, category))

    def set(self, category, klass):
        """register a class"""
        self[category][klass.id] = klass

    def list(self, category):
        """list available object's names registered"""
        return tuple(self[category])

    def define_category(self, category):
        """define a new class of registered objects"""
        assert not self.has_key(category)
        self[category] = {}

REGISTRY = Registry()

# testing classes
REGISTRY.define_category('repository')
REGISTRY.define_category('preprocessor')
REGISTRY.define_category('checker')

# access point functions
register = REGISTRY.set
list_registered = REGISTRY.list
get_registered = REGISTRY.get

del REGISTRY

class ConfigError(Exception):
    """exception due to a wrong user configuration"""

class NotSupported(Exception):
    """a feature is not supported by an implementation"""

class SetupException(Exception):
    """raised in the setup step"""
