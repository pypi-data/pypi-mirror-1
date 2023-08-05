############################################################################
#    Copyright (C) 2007 by William Waites <ww@styx.org>                    #
#                                                                          #
#    This program is free software; you can redistribute it and/or modify  #
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
pkg_config = {
	'name': 'django_options',
	'author': 'William Waites',
	'author_email': 'ww@styx.org',
	'url': 'http://www.haagenti.com/',
	'description': 'MetaOptions',
	'long_description': """
MetaOptions for Django Objects
	""",
	'packages': ['django.contrib.options'],
	'license': 'GPL',
	'platforms': ['all'],
}

if __name__ == '__main__':
	from distutils.core import setup
	from os import popen
	fp = popen("hg tip | awk '/^changeset:/ { print $2; }' | cut -d: -f1")
	rev = fp.read().strip()
	fp.close()
	pkg_config['version'] = 'r%s' % (rev)
	setup(**pkg_config)
