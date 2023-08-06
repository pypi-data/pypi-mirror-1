"""checker for HTML files, mxTidy based


:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import re

from apycotbot import register
from apycotbot.utils import SUCCESS, FAILURE
from apycotbot.checkers import AbstractFilteredFileChecker

class HTMLChecker(AbstractFilteredFileChecker):
    """check syntax of HTML files"""
    
    id = 'html_tidy'

    ignore = [
        'unknown attribute "xmlns:metal"',
        'unknown attribute "xmlns:tal"',
        'unknown attribute "xmlns:i18n"',
    
        '<tal:block> is not recognized',
        '<metal:block> is not recognized',
        'tal:block is not recognized',
        'metal:block is not recognized',
    
        '<html> has XML attribute "xml:lang"',
        'inserting missing \'title\' element',
        'discarding unexpected ',
        'trimming empty ',
    
        'This document has errors that must be fixed before',
        'using HTML Tidy to generate a tidied up version.',
    ]
 
    unknown_attr_rgx = re.compile('unknown attribute "(tal|metal|i18n):')
    checked_extensions = ('.htm', '.html')
        
    def check_file(self, filepath):
        """check a single file
        return true if the test succeeded, else false.
        """
        data = open(filepath.read())
        errors = tidy(data, output_markup=0, quiet=1)[-1]
        status = SUCCESS
        if errors:
            for line in errors.splitlines():
                line = line.strip()
                # ignore blanks
                if not line:
                    continue
                # loop through each error checking to see if its there
                # thanks Alan Runyan
                for msg in self.ignore:
                    if line.find(msg) > -1:
                        break
                else:
                    # re ignore
                    if self.unknown_attr_rgx.search(line):
                        continue
                    # that's really an error
                    status = FAILURE
                    # FIXME line no
                    self.writer.error(line, path=filepath)
        return status          
        
    def version_info(self):
        """hook for checkers to add their version information"""
        self.record_version_info('mx_tidy', tidy.__version__)

try:
    from mx.Tidy import tidy
    register('checker', HTMLChecker)
    HAS_TIDY = 1
except ImportError:
    HAS_TIDY = 0
