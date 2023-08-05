############################################################################
#    Copyright (C) 2007 by William Waites <ww@irl.styx.org>                #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as               #
#    published by the Free Software Foundation; either version 2 of the    #
#    License, or (at your option) any later version.                       #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public             #
#    License along with this program; if not, write to the                 #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

from glob import glob
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

pkg_config = {
	'name': 'osg',
	'version': '20071216',
	'author': 'William Waites',
	'author_email': 'ww@styx.org',
	'url': 'http://www.irl.styx.org/hgweb.py/osg/',
	'keywords': 'Directed Graph, OpenSocial, Django',
	'description': 'Directed Graph and OpenSocial Data API implementation for Django',
	'long_description': """
Core Directed Graph and OpenSocial Data API implementation.

OpenSocial Data API implementation is preliminary since it has
not yet been stabilized by Google.

Includes implementation of a generative algorithm for feedback 
network creation based on:

D. R. White, N. Kejzar, C. Tsallis, J. D. Farmer, and S. D. White.
"A Generative Model for Feedback Networks."
Physical Review E 73(1) (2006): Art. No. 016119 Part 2.
	""",
	'packages': ['osg'],
	'license': 'GPL',
	'platforms': ['all'],
}

if __name__ == '__main__':
	from sys import argv
	setup(**pkg_config)
