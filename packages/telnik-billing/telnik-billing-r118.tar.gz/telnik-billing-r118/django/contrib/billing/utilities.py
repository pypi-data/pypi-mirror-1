##########################################################################
#    Copyright (C) 2006, 2007 William Waites <ww@styx.org>
#    Copyright (C) 2006, 2007 Dmytri Kleiner <dk@trick.ca>
#    Copyright (C) 2006, 2007 Haagenti Group Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation; either version 2 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public
#    License along with this program; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
##########################################################################

def getattr_anyhow(obj, attr):
	parts = attr.split('__')
	cur = obj
	for part in parts:
		cur = getattr(cur, part)
		if callable(cur):
			cur = cur()
	return cur

def pFloat(number='0.0'):
	"""
	portable float converter
	"""
	from django.conf import settings
	if settings.DATABASE_ENGINE == 'sqlite3':
		number = float(number)
	else:
		from decimal import Decimal
		number = Decimal(str(number))
	return number

def seconds2str(value):
	seconds = int(value)
	minutes = (seconds / 60) % 60
	hours   = (seconds / 3600) % 24
	days    = (seconds / 86400) % 7
	weeks   = (seconds / 604800)
	seconds = seconds % 60

	ret = ""
	if weeks:
		ret = ' '.join((ret, '%sw' % (weeks,)))
	if days:
		ret = ' '.join((ret, '%sd' % (days,)))
	ret = ' '.join((ret, '%02d:%02d:%02d' % (hours, minutes, seconds)))
	return ret.strip()
