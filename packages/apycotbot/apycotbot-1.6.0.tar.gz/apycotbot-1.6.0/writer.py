"""Writer sending data to a cubicweb instance which store it and may be used
to display reports

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import logging
import traceback
from datetime import datetime
from StringIO import StringIO

from logilab.mtconverter import xml_escape

REVERSE_SEVERITIES = {
    logging.DEBUG :   u'DEBUG',
    logging.INFO :    u'INFO',
    logging.WARNING : u'WARNING',
    logging.ERROR :   u'ERROR',
    logging.FATAL :   u'FATAL'
    }

class DataWriter(object):
    """print execution message on stderr and store Test execution data to
    a CubicWeb instance (using the apycot cube)
    """

    def __init__(self, cnxh, config_eid):
        self._cnxh = cnxh
        # eid of the TestConfig entity
        self._cfg_eid = config_eid
        self._log_stack = []

    def debug(self, *args, **kwargs):
        """log an info"""
        self.log(logging.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        """log an info"""
        self.log(logging.INFO, *args, **kwargs)

    def warning(self, *args, **kwargs):
        """log a warning"""
        self.log(logging.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        """log an error"""
        self.log(logging.ERROR, *args, **kwargs)

    def fatal(self, *args, **kwargs):
        """log a fatal error"""
        self.log(logging.FATAL, *args, **kwargs)

    def start_test(self, branch):
        if branch is not None:
            branch = unicode(branch)
        self._ex_eid = self._cnxh.execute(
            'INSERT TestExecution X: X starttime %(starttime)s, '
            'X branch %(branch)s, X using_config CFG WHERE CFG eid %(x)s',
            {'starttime': datetime.now(), 'branch': branch, 'x': self._cfg_eid},
            'x')[0][0]
        self._cnxh.commit()
        self._log_stack.append([])

    def set_exec_status(self, status):
        self._cnxh.execute(
            'SET X status %(status)s WHERE X eid %(x)s',
            {'status': status, 'x': self._ex_eid}, 'x')
        self._cnxh.commit()

    def end_test(self, archived=False):
        """end of the test execution"""
        log = self._log_stack.pop()
        self._cnxh.execute(
            'SET X endtime %(endtime)s, X log %(log)s, X status %(status)s '
            'WHERE X eid %(x)s',
            {'endtime': datetime.now(), 'log': u'\n'.join(log),
             'status': archived and u'archived' or u'done',
             'x': self._ex_eid}, 'x')
        self._cnxh.commit()

    def start_check(self, name, options):
        self._cc_eid = self._cnxh.execute(
            'INSERT CheckResult X: X name %(name)s, X status "processing", '
            'X starttime %(starttime)s, X during_execution AE '
            'WHERE AE eid %(x)s',
            {'name': self._unicode(name), 'starttime': datetime.now(),
             'x': self._ex_eid},
            'x')[0][0]
        for name, value in options.iteritems():
            self.raw(name, value, 'option', commit=False)
        self._cnxh.commit()
        self._log_stack.append([])

    def end_check(self, status):
        """end of the latest started check"""
        log = self._log_stack.pop()
        self._cnxh.execute(
            'SET X status %(status)s, X endtime %(endtime)s, X log %(log)s '
            'WHERE X eid %(x)s',
            {'status': self._unicode(status), 'endtime': datetime.now(),
             'log': '\n'.join(log), 'x': self._cc_eid},
            'x')
        self._cnxh.commit()

    def _msg_info(self, *args, **kwargs):
        path = kwargs.pop('path', None)
        line = kwargs.pop('line', None)
        tb = kwargs.pop('tb', False)
        assert not kwargs
        if len(args) > 1:
            args = [self._unicode(string) for string in args]
            msg = args[0] % tuple(args[1:])
        else:
            assert args
            msg = args[0]
        if tb:
            stream = StringIO()
            traceback.print_exc(file=stream)
            msg += '\n' + stream.getvalue()
        return path, line, msg

    def execution_info(self, *args, **kwargs):
        msg = self._msg_info(*args, **kwargs)[-1]
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        print msg

    def log(self, severity, *args, **kwargs):
        """log a message of a given severity"""
        path, line, msg = self._msg_info(*args, **kwargs)
        encodedmsg = u'%s\t%s\t%s\t%s<br/>' % (severity, path or u'',
                                               line or u'', xml_escape(msg))
        self._log_stack[-1].append(encodedmsg)

    def raw(self, name, value, type=None, commit=True, check_data=True):
        """give some raw data"""
        if check_data and hasattr(self, '_cc_eid'):
            x = self._cc_eid
        else:
            x = self._ex_eid
        rset = self._cnxh.execute(
            'INSERT CheckResultInfo X: X label %(label)s, X value %(value)s, '
            'X type %(type)s, X for_check CHK WHERE CHK eid %(x)s',
            {'label': self._unicode(name), 'value': self._unicode(value),
             'type': type and unicode(type), 'x': x}, 'x')
        assert rset
        if commit:
            self._cnxh.commit()

    def link_to_revision(self, environment, vcsrepo):
        revision = vcsrepo.revision()
        if revision:
            if not self._cnxh.execute(
                'SET X using_revision REV '
                'WHERE X eid %(x)s, REV changeset %(cs)s, PE eid %(pe)s, '
                'PE local_repository R, REV from_repository R',
                {'x': self._ex_eid, 'cs': revision,
                 'pe': environment.eid}, ('x', 'pe')):
                self.raw(repr(vcsrepo), revision, 'revision')

    def _unicode(self, something):
        if isinstance(something, str):
            return unicode(something, 'utf-8', 'replace')
        if not isinstance(something, unicode):
            return unicode(something)
        return something

    def exec_id(self):
        return self._ex_eid
