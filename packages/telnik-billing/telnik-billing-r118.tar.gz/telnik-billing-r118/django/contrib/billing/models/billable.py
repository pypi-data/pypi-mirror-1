#############################################################################
#    Copyright (C) 2007 William Waites <ww@styx.org>                        #
#    Copyright (C) 2007 Dmytri Kleiner <dk@trick.ca>                        #
#    Copyright (C) 2007 Haagenti Group Inc.                                 #
#                                                                           #
#    This program is free software; you can redistribute it and#or modify   #
#    it under the terms of the GNU General Public License as                #
#    published by the Free Software Foundation; either version 2 of the     #
#    License, or (at your option) any later version.                        #
#                                                                           #
#    This program is distributed in the hope that it will be useful,        #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#    GNU General Public License for more details.                           #
#                                                                           #
#    You should have received a copy of the GNU General Public              #
#    License along with this program; if not, write to the                  #
#    Free Software Foundation, Inc.,                                        #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.              #
#############################################################################
from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ['DeferRecord', 'Billable', 'Billables', "DetailAlreadyExists", "get_billables"]

class DeferRecord(Exception):
	"""
	An error to be raised when recording is not possible at the moment
	and may be passed over again at some time in the future
	"""

class DetailAlreadyExists(Exception):
	"""DetailAlreadyExists"""

class Billable:
	"""
	>>> from django.contrib.billing.options import BillingOptions
	>>> class ExampleDetail(Billable, Model):
	...     class Billing(BillingOptions)
	...         ### required options
	...         dataType = 'PACKAGE-DETAIL-TYPE'
	...         dataKeys = ('property1', 'property2')
	...         ### defaulted optional options
	...         chargeTime = 'timestamp'
	...         charge = 'charge'
	...         chargeCurrency = 'chargeCurrency'
	...         chargeType = 'chargeType'
	...         chargedUnits = 'chargedUnits'
	...         chargeableUnits = 'chargeableUnits'
	...         description = 'description'
	...
	# data_type must be globally unique as it is used for the calculation of
	# the detail's hexdigest
	#
	# data_keys must be the set of properties on the data that uniquely 
	# and reproducibly describes it. the properties referenced may be
	#
	# WARNING: changing data_type or data_keys after details exist will
	# potentially invalidate all of your data. They are used to calculate the
	# detail's unique fingerprint which is not supposed to change. Ever.
	"""
	@staticmethod
	def save(self):
		from django.contrib.billing.digest import hexdigest
		digest = hexdigest(self)
		if self._default_manager.filter(hexdigest = digest).count():
			raise DetailAlreadyExists("Detail already exists with hexdigest %s in Database" % (digest,))
		if self.hexdigest and digest != self.hexdigest:
			raise DetailAlreadyExists("Hexdigest changed! %s was %s" % (digest, self.hexdigest))
		self.hexdigest = digest
		models.Model.save(self)

	@staticmethod
	def update(self):
		from django.contrib.billing.digest import hexdigest
		digest = hexdigest(self)
		if digest != self.hexdigest:
			raise DetailAlreadyExists("Hexdigest changed! %s was %s" % (digest, self.hexdigest))
		models.Model.save(self)

	@staticmethod
	def rehash(self):
		from django.contrib.billing.digest import hexdigest
		self.hexdigest = hexdigest(self)
		models.Model.save(self)

	@staticmethod
	def item(self):
		from django.contrib.billing.models import ItemRecord
		return ItemRecord.objects.get(hexdigest = self.hexdigest)
	
class Billables:
	"""
	>>> for implementation, name in Billables():
        ...
	"""
	def __iter__(self):
		for model in get_billables():
			implementation = '.'.join((model._meta.app_label,model._meta.object_name))
			yield (implementation, model._meta.verbose_name)

def get_billables():
	from django.db.models.loading import get_apps, get_models
	for app in get_apps():
		for model in get_models(app):
			if hasattr(model._meta, 'billing'):
				yield model
