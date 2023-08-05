###########################################################################
#	 Copyright (C) 2003-2007 William Waites <ww@styx.org>
#	 Copyright (C) 2006, 2007 Haagenti Group Inc.
#	 Copyright (C) 2004, 2005 Consultants Ars Informatica S.A.R.F.
#
#	 This program is free software; you can redistribute it and/or modify
#	 it under the terms of the GNU General Public License as
#	 published by the Free Software Foundation; either version 2 of the
#	 License, or (at your option) any later version.
#
#	 This program is distributed in the hope that it will be useful,
#	 but WITHOUT ANY WARRANTY; without even the implied warranty of
#	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	 GNU General Public License for more details.
#
#	 You should have received a copy of the GNU General Public
#	 License along with this program; if not, write to the
#	 Free Software Foundation, Inc.,
#	 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###########################################################################

__all__ = ['hexdigest', 'Unimplemented']

"""
Objects used in the telnik framework, particularly billing details
must be uniquely and globally identifiable. This is done by mandating
the implementation of a 'data_type' class attribute which is a string
representing the data type of the object and should be unique among
all objects, as well as a 'data_keys' list. 'data_keys' is a list of
attributes on the object that are to be used to calculate the digest.

>>> class A:
...   something = 'abc123'
...   def __repr__(self):
...     return '<A>'
...
>>> a = A()
>>> hexdigest(a)
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
  File "/usr/lib/python2.4/site-packages/django/contrib/billing/digest.py", line 44, in hexdigest
    raise Unimplemented('Please fill in data_type and data_keys on %s' % (obj,))
Unimplemented: Please fill in data_type and data_keys on <A>
>>> from django.contrib.billing.options import BillingOptions
>>> class B:
...   class Billing(BillingOptions):
...       dataType = 'TEST_DATA_TYPE'
...       dataKeys = ('a__something', 'b')
...   def __init__(self, **kw):
...     self.__dict__.update(kw)
... 
>>> b = B(a = a, b = 2)
>>> hexdigest(b)
'208eae134320117459e11ea73eb89f0b719e5f39'
>>>
"""
class Unimplemented(Exception):
	"""Hex Digest is unimplemented"""

def hexdigest(obj):
	"""
	Calculates and returns the globally unique fingerprint for
	the given object.
	"""
	from datetime import datetime, date, time
	from urllib import urlencode
	import sha
	from django.contrib.billing.utilities import getattr_anyhow

	if not hasattr(obj._meta, 'billing'):
		raise Unimplemented('Please fill in a Billing options class on %s' % (obj,))
	opts = obj._meta.billing
	if not hasattr(opts, 'dataType') or not hasattr(opts, 'dataKeys'):
		raise Unimplemented('Please fill in dataType and dataKeys on %s' % (obj,))
	
	data = [('data_type', obj._meta.billing.dataType)]
	keys = list(obj._meta.billing.dataKeys)
	keys.sort()
	for key in keys:
		val = getattr_anyhow(obj, key)
		if isinstance(val, datetime) or isinstance(val, date) or isinstance(val, time):
			val = val.isoformat()
		data.append((key, val))
	qs = urlencode(data)
	hash = sha.new()
	hash.update(qs)
	return hash.hexdigest()
