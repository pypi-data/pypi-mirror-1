# pylint: disable-msg=W0622
"""some common utilities shared by different APyCoT modules

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import os
import sys
import stat
import logging
from subprocess import PIPE, STDOUT, Popen
from tempfile import TemporaryFile

from Pyro import errors

from logilab.common.logging_ext import set_log_methods
from logilab.common.pyro_ext import ns_group_and_id

from cubicweb import BadConnectionId
from cubicweb.dbapi import ProgrammingError, connect
from cubicweb.toolsutils import read_config

from apycotbot import MODE, ConfigError, SetupException


# shared options ##############################################################

PYRO_NS_OPTIONS = (
    # pyro name server
    ('pyro-ns-host',
     {'type' : 'string',
      'default': '',
      'help': 'Pyro name server\'s host where the bot is registered. If not '\
      'set, will be detected by a broadcast query. You can also specify a '\
      'port using <host>:<port> notation.',
      'group': 'pyro-name-server', 'inputlevel': 1,
      }),
)

PYRO_OPTIONS = (
    ('pyro-id',
     {'type' : 'string',
      'default': 'apycotbot',
      'help': 'identifier of the apycot bot in the pyro name-server.',
      'group': 'pyro-server', 'inputlevel': 2,
      }),
) + PYRO_NS_OPTIONS

CW_OPTIONS = (
    ('cw-inst-id',
     {'type' : 'string', 'short': 'a',
      'help': 'identifier of the CubicWeb instance used to store tests '\
      'configuration and results in the pyro name-server.',
      'default': 'apycot',
      'group': 'main', 'inputlevel': 0,
      }),
)

TEST_OPTIONS = (
    ('plugins',
     {'type' : 'csv',
      'help': 'comma separated list of plugins (eg python modules) that should be loaded at startup',
      'group': 'main', 'inputlevel': 2,
      }),

    ('test-dir',
     {'type' : 'file',
      'default': '/tmp',
      'help': 'directory where the test environment will be built',
      'group': 'main', 'inputlevel': 2,
      }),
    ('archive-dir',
     {'type' : 'file',
      'default': '/tmp',
      'help': 'directory where the test environment archive will be stored',
      'group': 'main', 'inputlevel': 2,
     }),
)

RESOURCES_OPTIONS = (
    ('max-cpu-time',
     {'type' : 'time',
      'default': None,
      'help': 'maximum CPU Time in second that may be used to execute a test.',
      'group': 'process-control', 'inputlevel': 2,
      }),
    ('max-time',
     {'type' : 'time',
      'default': None,
      'help': 'maximum Real Time in second that may be used to execute a test.',
      'group': 'process-control', 'inputlevel': 2,
      }),
    ('max-memory',
     {'type' : 'bytes',
      'default': None,
      'help': 'maximum Memory in bytes the test can allocate.',
      'group': 'process-control', 'inputlevel': 2,
      }),
    ('max-reprieve',
     {'type' : 'time',
      'default': 60,
      'help': 'delay in second while the test try to abort nicely (reporting '
      'the error and cleaning up the environement before it\'s killed).',
      'group': 'process-control', 'inputlevel': 2,
      }),
)

# cubicweb connection handling ################################################

class ConnectionHandler(object):
    """handle connection to a cubicweb repository"""

    if MODE == 'dev':
        _default_sources_file = os.path.expanduser('~/etc/apycotbot-cw-sources.ini')
    else:
        _default_sources_file = '/etc/apycotbot-cw-sources.ini'

    def __init__(self, cwinstid, nshost=None):
        if not cwinstid:
            raise ConfigError('you must specify main cubicweb instance '
                              'identifier in the configuration file or using '
                              'the --cw-inst-id option')
        nsgroup, instid = ns_group_and_id(cwinstid, defaultnsgroup=None)
        self.cw_pyro_instid = instid
        if os.path.exists(self._cw_sources_file):
            self._cnx_infos = read_config(self._cw_sources_file)
        else:
            self._cnx_infos = {}
        system_info = self._cnx_infos.setdefault(instid, {})
        if nsgroup:
            if not system_info.get('pyro-ns-group', nsgroup) == nsgroup:
                raise ConfigError('conflicting values for pyro-ns-group')
            system_info['pyro-ns-group'] = nsgroup
        if nshost and not 'pyro-ns-host' in system_info:
            system_info['pyro-ns-host'] = nshost
        self.cnx = None
        self._cu = None

    @property
    def _cw_sources_file(self):
        return os.environ.get('APYCOTBOTSOURCES', self._default_sources_file)

    def connect(self):
        mycnxinfo = self._cnx_infos[self.cw_pyro_instid]
        user = mycnxinfo.get('user', 'apycotbot')
        password = mycnxinfo.get('password', 'apycot')
        group = mycnxinfo.get('pyro-ns-group', None)
        host = mycnxinfo.get('pyro-ns-host', None)
        try:
            self.cnx = connect(self.cw_pyro_instid, user, password,
                                group=group, host=host, initlog=False)
            self._cu = self.cnx.cursor()
        except Exception, ex:
            self.critical('error while trying to connect to instance %r: %s',
                          self.cw_pyro_instid, ex)
            return None
        else:
            self.cnx.load_appobjects(cubes='apycot', subpath=('entities',),
                                     expand=False)
            return self.cnx

    def activated_tests(self):
        if self.cnx is None and not self.connect():
            raise Exception('can\'t list activated tests, can\'t connect to %s'
                            % (self.cw_pyro_instid))
        return self.execute(
            'Any X WHERE X is TestConfig, X in_state S, S name "activated"')

    def test_config(self, pename, tcname, reconnect=True):
        if self.cnx is None and not self.connect():
            raise Exception('can\'t start test %s, can\'t connect to %s'
                            % (tcname, self.cw_pyro_instid))
        try:
            # check test is known
            return self.execute('Any PE, PEN, TC, TCN WHERE TC use_environment PE, '
                                'PE name %(pename)s, TC name %(tcname)s, '
                                'PE name PEN, TC name TCN, '
                                'PE is ProjectEnvironment, TC is TestConfig',
                                {'pename': pename, 'tcname': tcname},
                                reconnect=reconnect).get_entity(0, 2)
        except IndexError:
            raise Exception('unknown test %s.%s' % (pename, tcname))

    def execute(self, rql, kwargs=None, cachekeys=None, reconnect=True):
        try:
            return self._cu.execute(rql, kwargs, cachekeys)
        except (BadConnectionId, errors.PyroError):
            if reconnect and self.connect():
                return self.execute(rql, kwargs, cachekeys, reconnect=False)
            raise

    def commit(self):
        self.cnx.commit()

    def close(self):
        if self.cnx is not None:
            try:
                self.cnx.close()
            except (ProgrammingError, BadConnectionId, errors.PyroError):
                pass

LOGGER = logging.getLogger('apycot.cubicweb')
set_log_methods(ConnectionHandler, LOGGER)

# check status ################################################################

class TestStatus(object):
    __all = {}

    def __init__(self, name, order, nonzero):
        self.name = name
        self.order = order
        self.nonzero = nonzero
        self.__all[name] = self

    def __int__(self):
        return self.order

    def __nonzero__(self):
        return self.nonzero

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<TestStatus %s>" % self.name

    def __cmp__(self, other):
        return cmp(int(self), int(other))

    @classmethod
    def get(cls, name):
        return cls.__all.get(name)

###############################
## Available Checker results ##
###############################

# keep order for bw compat
MISSING = TestStatus('missing', -10, False) # Checker not found
SKIPPED = TestStatus('skipped',  -5, False) # Checker not even launched
KILLED  = TestStatus('killed',   -3, False) # Checker killed (for limit reason)
ERROR   = TestStatus('error',    -1, False) # Unexpected error during chks exec
FAILURE = TestStatus("failure",   0, False) # Project failed the check
NODATA  = TestStatus('nodata',    2, False) # No data found in the project
PARTIAL = TestStatus('partial',   5, True)  # Project partially pass th check
SUCCESS = TestStatus('success',  10, True)  # Project succeed the check


# others ######################################################################

_MARKER = ()

class ApycotObject(object):
    """base class for apycot checkers / preprocessors"""
    options_def = ()
    status = None

    def __init__(self, writer, options=None):
        self.writer = writer
        self.options = options or {}

    @staticmethod
    def merge_status(global_status, status):
        if global_status is None:
            return status
        elif status is None:
            return global_status
        else:
            return min(global_status, status)

    def set_status(self, status):
        self.status = self.merge_status(self.status, status)

    def record_version_info(self, versionof, version):
        self.writer.raw(versionof, version, 'version')

    def get_option(self, option, default=_MARKER, msg=None):
        """return option's value or None, raise ConfigError if no default is
        provided and the option is not defined
        """
        value = self.options.get(option, default)
        if value is _MARKER:
            msg = msg or 'Missing %r option for %s %s' % (option, self.__type__,
                                                          self.id)
            raise ConfigError(msg)
        return value

    def check_options(self):
        """check options according to the required_options attributes
        """
        for optdict in self.options_def:
            assert hasattr(optdict, 'get'), "optdict : %s ; self.options : %s" % (optdict, self.options)
            if optdict.get('required') and not self.get_option(optdict['name']):
                raise ConfigError('missing/empty value for option %r'
                                  % optdict['name'])


class EnvironmentTrackerMixin:
    """track environment change to be able to restore it latter

    sys.path is synchronized with the PYTHONPATH environment variable
    """

    writer = None

    def __init__(self, writer=None):
        self._tracks = {}
        self.writer = writer

    def update_env(self, key, envvar, value, separator=None):
        """update an environment variable"""
        envvar = envvar.upper()
        orig_value = os.environ.get(envvar)
        if orig_value is None:
            orig_value = ''
        uid = self._make_key(key, envvar)
        assert not self._tracks.has_key(uid)
        if separator is not None:
            if orig_value:
                orig_values = orig_value.split(separator)
            else:
                orig_values = [] # don't want a list with an empty string
            if not value in orig_values:
                orig_values.insert(0, value)
                self._set_env(uid, envvar, separator.join(orig_values))
        elif orig_value != value:
            self._set_env(uid, envvar, value)

    def clean_env(self, key, envvar):
        """reinitialize an environment variable"""
        envvar = envvar.upper()
        uid = self._make_key(key, envvar)
        if self._tracks.has_key(uid):
            orig_value = self._tracks[uid]
            if envvar == 'PYTHONPATH':
                update_path(os.environ.get(envvar), orig_value)
            if self.writer:
                self.writer.debug('Reset %s=%r', envvar, orig_value)
            if orig_value is None:
                del os.environ[envvar]
            else:
                os.environ[envvar] = self._tracks[uid]
            del self._tracks[uid]

    def _make_key(self, key, envvar):
        """build a key for an environment variable"""
        return '%s-%s' % (key, envvar)

    def _set_env(self, uid, envvar, value):
        """set a new value for an environment variable
        """
        if self.writer:
            self.writer.debug('Set %s=%r', envvar, value)
        orig_value = os.environ.get(envvar)
        self._tracks[uid] = orig_value
        os.environ[envvar]  = value
        if envvar == 'PYTHONPATH':
            update_path(orig_value, value)


def clean_path(path):
    """remove trailing path separator from path"""
    if path and path[-1] == os.sep:
        return path[:-1]
    return path

def update_path(old_path, new_path):
    """update sys.path"""
    if old_path is not None:
        for path in old_path.split(os.pathsep):
            try:
                sys.path.remove(clean_path(path))
            except ValueError:
                continue
    if new_path is not None:
        new_path = new_path.split(os.pathsep)
        new_path.reverse()
        for path in new_path:
            sys.path.insert(0, clean_path(path))


# base class for external command #############################################


class SimpleOutputParser(ApycotObject):
    non_zero_status_code = ERROR
    status = SUCCESS

    def __init__(self, writer, options=None):
        super(SimpleOutputParser, self).__init__(writer, options)
        self.unparsed = None
        self.path = None

    def map_message(self, mtype, msg):
        if mtype == 'W':
            self.writer.warning(msg, path=self.path)
        elif mtype == 'E':
            self.writer.error(msg, path=self.path)
            self.set_status(FAILURE)
        elif mtype in 'F':
            self.writer.fatal(msg, path=self.path)
            self.set_status(FAILURE)
        elif msg:
            self.unparsed.append(msg)

    def parse_line(self, line):
        line_parts = line.split(':', 1)
        if len(line_parts) > 1:
            mtype, msg = line_parts
            self.map_message(mtype.strip(), msg.strip())
        else:
            self.unparsed.append(line.strip())

    def parse(self, stream):
        self.unparsed = []
        self._parse(stream)
        return self.status

    def _parse(self, stream):
        for line in stream:
            line = line.strip()
            if line:
                self.parse_line(unicode(line, 'utf8', 'replace'))


class Command(ApycotObject):
    non_zero_status_code = ERROR
    status = SUCCESS

    def __init__(self, writer, command, parsed_content='merged',
                 raises=False, shell=False, path=None):
        super(Command, self).__init__(writer)
        assert command, command
        self.command = command
        self.parsed_content = parsed_content
        self.raises = raises
        self.shell = shell
        self.path = None
        self._cmd_printed = False

    @property
    def commandstr(self):
        if not isinstance(self.command, basestring):
            return ' '.join(self.command)
        return self.command

    def run(self):
        """actually run the task by spawning a subprocess"""
        os.environ['LC_ALL'] = 'fr_FR.UTF-8' # XXX force utf-8
        outfile = TemporaryFile(mode='w+', bufsize=0)
        if self.parsed_content == 'merged':
            errfile = STDOUT
        else:
            errfile = TemporaryFile(mode='w+', bufsize=0)
        cmd = Popen(self.command, bufsize=0, stdout=outfile, stderr=errfile,
                    stdin=open('/dev/null', 'a'), shell=self.shell)
        cmd.communicate()
        if self.parsed_content == 'merged':
            outfile.seek(0)
            self.handle_output(cmd.returncode, outfile, None)
        else:
            for stream in (outfile, errfile):
                stream.seek(0)
            if not os.fstat(errfile.fileno())[stat.ST_SIZE]:
                errfile = None
            if not os.fstat(outfile.fileno())[stat.ST_SIZE]:
                outfile = None
            self.handle_output(cmd.returncode, outfile, errfile)
        return self.status

    def handle_output(self, status, stdout, stderr):
        stdout, stderr, unparsed = self.process_output(stdout, stderr)
        cmd = self.commandstr
        path = self.path or cmd
        print 'handle output', cmd
        if status:
            if status > 0:
                msg = u'`%s` returned with status : %s' % (cmd, status)
                cmd_status = self.non_zero_status_code
            else:
                # negative status mean the process have been killed by a signal
                msg = u'`%s` killed by signal %s' % (cmd, status)
                # Get the signal number
                status *= -1
                cmd_status = KILLED
                # XXX we need detection of common limit here
            if self.raises:
                raise SetupException(msg)
            msg = self.append_output_messages(msg, stdout, stderr, unparsed)
            self.writer.error(msg, path=path)
            self.set_status(cmd_status)
        else:
            msg = self.append_output_messages(u'`%s` executed successfuly' % cmd,
                                              stdout, stderr, unparsed)
            self.writer.debug(msg, path=path)

    def append_output_messages(self, msg, stdout, stderr, unparsed):
        if stdout is not None:
            stdout = unicode(stdout.read(), 'utf8', 'replace')
            if self.parsed_content == 'merged':
                msg +=u'\noutput:\n%s' % stdout
            else:
                msg +=u'\nstandard output:\n%s' % stdout
        if stderr is not None:
            stderr = unicode(stderr.read(), 'utf8', 'replace')
            msg +=u'\nerror output:\n%s' % stderr
        if unparsed:
            msg +=u'\nunparsed output:\n%s' % unparsed
        return msg

    def process_output(self, stdout, stderr):
        return stdout, stderr, None


class ParsedCommand(Command):
    def __init__(self, writer, command, parsercls=SimpleOutputParser, **kwargs):
        Command.__init__(self,  writer, command, **kwargs)
        self.parser = parsercls(writer)
        self.parser.path = self.path
        self.non_zero_status_code = self.parser.non_zero_status_code

    def process_output(self, stdout, stderr):
        if stdout is not None and self.parsed_content in ('stdout', 'merged'):
            self.status = self.parser.parse(stdout)
            return None, stderr, u'\n'.join(self.parser.unparsed)
        if stderr is not None and self.parsed_content == 'stderr':
            self.status = self.parser.parse(stderr)
            return stdout, None, u'\n'.join(self.parser.unparsed)
        return stdout, stderr, None
