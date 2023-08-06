"""checker for Page Template files


:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from os.path import dirname, join

from apycotbot import register
from apycotbot.checkers.chks_html import HTMLChecker

class ZPTChecker(HTMLChecker):
    """check syntax of Page Template file
    """
    
    id = 'pt_syntax'
    checked_extensions = ('.pt', '.zpt', '.cpt')

    def check_file(self, filepath):
        """check a single file
        return true if the test succeeded, else false.
        """
        data = open(filepath).read()
        zpt = ZopePageTemplate.ZopePageTemplate('test',  text=data)
        status = 1
        for msg in zpt._v_errors:
            # FIXME line no
            self.writer.error(msg, path=filepath)
            status = 0
        for msg in zpt._v_warnings:
            self.writer.warning(msg, path=filepath)
        html_status = HTMLChecker.check_file(self, filepath, self.writer)
        return status and html_status
    
    def version_info(self):
        """hook for checkers to add their version information"""
        HTMLChecker.version_info(self)
        vfile = open(join(dirname(ZopePageTemplate.__file__), 'version.txt'))
        version = vfile.read().strip()
        self.writer.raw('page_templates_version', version, 'version')


try:
    try:
        import Zope2 as Zope
    except ImportError:
        import Zope
        
    if hasattr(Zope, 'startup'):
        try:
            Zope.startup()
        except: # FIXME: startup doesn't finish correctly, but I don't know why...
            pass
        
    from Products.PageTemplates import ZopePageTemplate
    register('checker', ZPTChecker)
    
except ImportError:
    
    pass
