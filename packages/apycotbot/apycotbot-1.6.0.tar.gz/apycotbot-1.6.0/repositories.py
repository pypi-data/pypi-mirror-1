"""Some standard sources repositories, + factory function

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import os
from os import path as osp
from time import localtime

from logilab.devtools.vcslib.svn import SVNAgent
from logilab.devtools.vcslib.cvs import CVSAgent
from logilab.devtools.vcslib.hg import HGAgent, split_url_or_path

from apycotbot import register, get_registered, ConfigError, NotSupported


SUPPORTED_REPO_TYPES = ('cvs', 'svn', 'hg', 'null', 'fs', 'mock')


def get_repository(attrs):
    """factory method: return a repository implementation according to
    <attrs> (a dictionary)
    """
    repo_type = attrs.pop('repository_type', None)
    if repo_type is None:
        if ':' not in attrs.get('repository', ''):
            repo_type, repo = 'null', None
            #warn("no repository found using null instead", RuntimeWarning)
        else:
            repo_type, repo = attrs['repository'].split(':', 1) # 'cvs'
            attrs['repository'] = repo
    assert repo_type in SUPPORTED_REPO_TYPES, repo_type
    return get_registered('repository', repo_type)(attrs)

class VersionedRepository:
    """base class for versionned repository"""

    id = None
    agent_class = None
    default_branch = None

    def __init__(self, attrs):
        try:
            self.repository = attrs.pop('repository')
        except KeyError, ex:
            raise ConfigError('Missing %s option: %s' % (ex, attrs))
        if not self.repository:
            raise ConfigError('Repository must be specified (%s)' % (attrs,))
        self.path = attrs.pop('path', '')
        branch = attrs.pop('branch', None)
        if branch is None:
            branch = self.default_branch
        self.branch = branch
        if self.agent_class is not None:
            self.agent = self.agent_class()

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.repository == other.repository and
                self.path == other.path and
                self.branch == other.branch)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        """get a string synthetizing the location"""
        myrepr = '%s:%s' % (self.id, self.repository)
        if self.path:
            myrepr += '/' + self.path
        if self.branch:
            myrepr += '@%s' % self.branch
        return myrepr

    def co_path(self):
        """return the relative path where the project will be located in the
        test environment
        """
        if self.path:
            return osp.split(self.path.rstrip(osp.sep))[1]
        return split_url_or_path(self.repository)[1]

    def co_command(self, quiet=True):
        """return a command that may be given to os.system to check out a given
        package
        """
        return self.agent.checkout(self.repository, self.path, self.branch,
                                   quiet=quiet)

    def co_move_to_branch_command(self, quiet=True):
        return None

    def log_info(self, from_date, to_date):
        """get checkins information between <from_date> and <to_date>

        Both date should be local time (ie 9-sequence) or epoch time (ie float)

        return an iterator on `logilab.devtools.vcslib.CheckInInfo` instances
        """
        from_date, to_date = self.normalize_date(from_date, to_date)
        return self.agent.log_info(self.repository, from_date, to_date,
                                   self.path, self.branch)

    def representative_attributes(self):
        """return a dictionary representing this repository state, so it can be
        recreated latter
        """
        result = self.__dict__.copy()
        result['repository_type'] = self.id
        result.pop('agent', None)
        return result

    def normalize_date(self, from_date, to_date):
        """get dates as float or local time and return the normalized dates as
        local time tuple to fetch log information from <from_date> to <to_date>
        included
        """
        if isinstance(from_date, float):
            from_date = localtime(from_date)
        if isinstance(to_date, float):
            to_date = localtime(to_date)
        return (from_date, to_date)

    def revision(self):
        """return revision of the working directory"""
        return None


class CVSRepository(VersionedRepository):
    """extract sources/information for a project from a CVS repository"""
    id = 'cvs'
    agent_class = CVSAgent

register('repository', CVSRepository)


class SVNRepository(VersionedRepository):
    """extract sources/information for a project from a SVN repository"""
    id = 'svn'
    agent_class = SVNAgent

    def co_path(self):
        """return the relative path where the project will be located
        in the test environment
        """
        # only url components
        if self.branch:
            return self.branch.rstrip('/').rsplit('/', 1)[1]
        if self.path:
            return self.path.rstrip('/').rsplit('/', 1)[1]
        return self.repository.rstrip('/').rsplit('/', 1)[1]



register('repository', SVNRepository)


class HGRepository(VersionedRepository):
    """extract sources/information for a project from a Mercurial repository"""
    id = 'hg'
    agent_class = HGAgent
    default_branch = "default"

    def co_path(self):
        """return the relative path where the project will be located in the
        test environment
        """
        copath = split_url_or_path(self.repository)[1]
        if self.path:
            return osp.join(copath, self.path)
        return copath

    def co_command(self, quiet=True):
        """return a command that may be given to os.system to check out a given
        package
        """
        return self.agent.checkout(self.repository, self.path, quiet=quiet)

    def co_move_to_branch_command(self, quiet=True):
        # if branch doesn't exists, stay in default
        if self.branch:
            return 'cd %s; hg up %s' % (self.co_path(), self.branch)
        return None

    def revision(self):
        return self.agent.current_short_changeset(self.co_path())

register('repository', HGRepository)


class FSRepository(VersionedRepository):
    """extract sources for a project from the files system"""
    id = 'fs'
    def co_command(self, quiet=True):
        """return a command that may be os.systemed to check out a given package
        """
        return 'cp -R %s .' % self.repository

    def log_info(self, from_date, to_date):
        """get list of log messages

        a log information is a tuple
        (file, revision_info_as_string, added_lines, removed_lines)
        """
        raise NotSupported()

register('repository', FSRepository)


class NullRepository(FSRepository):
    """dependencies only"""
    id = 'null'

    def __init__(self, attrs):
        pass

    def co_command(self, quiet=True):
        """return a command that may be os.systemed to check out a given package
        """
        return None #can't be os.systemed

    def co_path(self):
        """return the relative path where the project will be located
        in the test environment
        """
        return self.path

    def representative_attributes(self):
        """return a dictionary representing this repository state, so it can be
        recreated latter
        """
        return {'repository_type': 'null'}

register('repository', NullRepository)

