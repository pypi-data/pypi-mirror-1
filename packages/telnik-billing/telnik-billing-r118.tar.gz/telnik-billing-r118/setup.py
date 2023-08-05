############################################################################
#    Copyright (C) 2004, 2005 by William Waites <ww@groovy.net>            #
#    Copyright (C) 2004, 2005 Consultants Ars Informatica S.A.R.F.         #
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

from distutils.command.install import INSTALL_SCHEMES

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
            scheme['data'] = scheme['purelib']

from glob import glob
pkg_config = {
	'name': 'telnik-billing',
	'author': 'William Waites, Dmytri Kleiner',
	'author_email': 'ww@styx.org, dk@trick.ca',
	'url': 'http://www.haagenti.com',
	'description': 'Telnik - Billing',
	'long_description': """
Telnik Billing Framework
	""",
	'packages': ['django.contrib.billing', 'django.contrib.billing.models', 'django.contrib.billing.views'],
	'data_files': [
		('django/contrib/billing/templates', glob('django/contrib/billing/templates/*.html')),
		('bin', ('scripts/billing_rerate', 'scripts/receipt_refresh')),
	],
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
