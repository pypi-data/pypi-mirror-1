# pylint: disable-msg=W0622
# Copyright (c) 2005 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""Framework for Automated Testing of Instant Messaging Agents"""

__revision__ = "$Id: __pkginfo__.py,v 1.3 2005-05-20 14:21:13 arthur Exp $"

modname = 'fatima'
numversion = (0, 2, 0)
version = '0.2.0'

license = 'GPL'
copyright = '''Copyright (c) 2005 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Sylvain Thenault"
author_email = "devel@logilab.fr"

short_desc = "tool to test instant messaging agent"
long_desc = """Framework for Automated Testing of Instant Messaging Agents :

read dialog specification from a file in a specific ReST format, connect to
IM server as a regular user and check the dialog against a connected bot.
"""
web = "http://www.logilab.org/projects/fatima"
ftp = "ftp://ftp.logilab.org/pub/fatima"
mailinglist = "mailto://qa-projects@logilab.org"
#from os.path import join

include_dirs = []


scripts = ['bin/imtestcli'] 

# debianize info
debian_maintainer = 'Sylvain Thenault'
debian_maintainer_email = 'sylvain.thenault@logilab.fr'
pyversions = ['2.4', '2.5']
