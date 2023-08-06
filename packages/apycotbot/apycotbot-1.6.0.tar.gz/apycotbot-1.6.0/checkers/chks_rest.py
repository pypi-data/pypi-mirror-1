# pylint: disable-msg=W0613
"""checkers for ReST files

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import re
import logging

try:
    from docutils import nodes, __version__ as docutils_version
    from docutils.frontend import OptionParser
    from docutils.parsers import rst
except ImportError:
    docutils_version = None
    
from apycotbot import register
from apycotbot.utils import SUCCESS, FAILURE
from apycotbot.writer import REVERSE_SEVERITIES
from apycotbot.checkers import AbstractFilteredFileChecker

class MyReporter:
    debug_flag = False
    def __init__(self, writer, path):
        self._writer = writer
        self._path = path
        self.errors = 0
    
    def attach_observer(self, observer):
        """ignore this method"""
    def detach_observer(self, observer):
        """ignore this method"""
    def notify_observers(self, message):
        """ignore this method"""

    def system_message(self, level, comment=None, category='',
                       *children, **attributes):
        """return a system_message object and log the message with the apycot
        framework
        """
        try:
            docutils_msg_type = REVERSE_SEVERITIES[level]
        except KeyError:
            docutils_msg_type = level
            level = logging.WARNING
        msg = nodes.system_message(comment, level=level,
                                   type=docutils_msg_type,
                                   *children, **attributes)
        line = msg.get('line')
        self._writer.log(level, comment, path=self._path, line=line)
        if level == logging.ERROR:
            self.errors += 1
        return msg

    def debug(self, comment=None, category='', *children, **attributes):
        """ignore debug messages"""

    def info(self, comment=None, category='', *children, **attributes):
        """
        Level-1, "INFO": a minor issue that can be ignored. Typically there is
        no effect on processing, and level-1 system messages are not reported.
        """
        return self.system_message(
              logging.INFO, comment, category, *children, **attributes)

    def error(self, comment=None, category='', *children, **attributes):
        """
        Level-3, "ERROR": an error that should be addressed. If ignored, the
        output will contain errors.
        """
        return self.system_message(
              logging.ERROR, comment, category, *children, **attributes)

    warning = severe = error

    
class ReSTChecker(AbstractFilteredFileChecker):
    """check syntax of ReST file
    """
    id = 'rest_syntax'
    checked_extensions = ('.txt', '.rst')

    def check_file(self, filepath):
        """check a single file
        return true if the test succeeded, else false.
        """
        parser = rst.Parser()
        options = OptionParser().get_default_values()
        
        # Set the halt_level to the error's level so we can get an Exception
        # docutils.frontend : 
        #       info = 1, warning = 2, error = 3, severe = 4, none = 5
        #options.debug = 0
        #options.halt_level = 2
        # We don't want the parser to warn us about anything
        #options.report_level = 5
        
        options.tab_width = 8
        options.pep_references = None
        options.rfc_references = None
        options.file_insertion_enabled = True
        source = file(filepath, 'rb').read()

        firstline = source.split('\n', 1)[0].strip()
        m = re.match(r'^\.\. \-\*\-(?P<params>.*)\-\*\-$', firstline)
        if m:
            params = m.group('params').strip()
            m = re.match(r'coding[=:]\s*(?P<encoding>[-\w.]+)', params)
            if m:
                encoding = m.group('encoding')
                source = source.decode(encoding)
        reporter = MyReporter(self.writer, filepath)
        doc = nodes.document(options, reporter, source=filepath)
        doc.note_source(source, -1)
        
        parser.parse(source, doc)
        if not reporter.errors:
            return SUCCESS
        return FAILURE
    
    def version_info(self):
        """hook for checkers to add their version information"""
        self.writer.raw('docutils_version', docutils_version, 'version')

if docutils_version is not None:
    register('checker', ReSTChecker)
