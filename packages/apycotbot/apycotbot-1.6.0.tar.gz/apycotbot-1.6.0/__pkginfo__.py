# pylint: disable-msg=W0622,C0103
"""apycotbot packaging information"""

distname = "apycotbot"
modname = "apycotbot"

numversion = (1, 6, 0)
version = '.'.join(str(num) for num in numversion)

license = 'GPL'
copyright = '''Copyright (c) 2003-2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"

short_desc = "Apycot bot client dedicated to launch test suites"
long_desc = """This version of apycot can now use the cubicweb framework."""

web = ''
ftp = ''
pyversions = ['2.4']

from os.path import join
scripts = (join('bin', 'apycotbot'),
           join('bin', 'apycotclient'))
