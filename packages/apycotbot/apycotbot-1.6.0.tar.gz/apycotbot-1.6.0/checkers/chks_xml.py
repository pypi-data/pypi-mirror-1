"""checkers for xml files (using lxml)

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

import logging

from lxml.etree import XMLParser, parse, ErrorLevels

from apycotbot import register
from apycotbot.utils import SUCCESS, FAILURE
from apycotbot.checkers import AbstractFilteredFileChecker

LXML_TO_LOGILAB_ERROR_CODE = {
    ErrorLevels.NONE : logging.INFO,
    ErrorLevels.WARNING : logging.WARNING,
    ErrorLevels.ERROR : logging.ERROR,
    ErrorLevels.FATAL: logging.FATAL,
}

class XmlFormChecker(AbstractFilteredFileChecker):
    """check well-formness of xml files"""
    id = 'xml_well_formed'
    checked_extensions = ('.xml',)
    parser = XMLParser(recover=True)
    
    def check_file(self, filepath):
        """check a single file
        return true if the test succeeded, else false.
        """
        parse(filepath, self.parser)
        if self.parser.error_log:
            for error in self.parser.error_log:
                self.writer.log(LXML_TO_LOGILAB_ERROR_CODE[error.level],
                                error.message, path=filepath, line=error.line)
            return FAILURE
        return SUCCESS
    
    def version_info(self):
        """hook for checkers to add their version information"""
        self.writer.raw('lxml_parser_version', self.parser.version, 'version')

register('checker', XmlFormChecker)


class XmlValidChecker(XmlFormChecker):
    """check validity of xml file
    """
    
    id = 'xml_valid'
    checked_extensions = ('.xml',)
    parser = XMLParser(recover=True, dtd_validation=True, load_dtd=True)

register('checker', XmlValidChecker)
