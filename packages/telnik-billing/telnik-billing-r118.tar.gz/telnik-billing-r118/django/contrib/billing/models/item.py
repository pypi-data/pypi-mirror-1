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
from django.contrib.forex.models import Currency
from django.contrib.billing.utilities import pFloat, getattr_anyhow
from account import Account, Consumer
from receipt import Receipt
from rate import Rating
from billable import DeferRecord

__all__ = ['ItemRecord']

class ItemRecordManager(models.Manager):
	def get_or_create(self, detail, *av, **kw):
		try:
			item = self.get(hexdigest = detail.hexdigest)
			return item, False
		except self.model.DoesNotExist:
			item = self.create(detail, *av, **kw)
			return item, True
		
	def create(self, detail, receipt = None, **kw):
		item = self.model(hexdigest = detail.hexdigest)
		if receipt:
			item.receipt = receipt
		self._update(item, detail, **kw)

	def update(self, item, detail, **kw):
		item = self.get(hexdigest = detail.hexdigest)
		self._update(item, detail, **kw)

	def _update(self, item, detail, sync = True):
		def _getattr(detail, attr):
			if hasattr(detail._meta.billing, attr):
				attr = getattr(detail._meta.billing, attr)
			return getattr_anyhow(detail, attr)
		
		for attrname in ('consumer', 'chargeDescription', 'chargeTime'):
			attr = _getattr(detail, attrname)
			setattr(item, attrname, attr)
			
		rateplan = item.consumer.account.rateplan
		chargeType = _getattr(detail, 'chargeType')
		chargeCurrency = _getattr(detail, 'chargeCurrency')
	
		if not isinstance(detail, models.Model):
			raise ValueError('%s must be a model' % (detail,))
		implementation = '.'.join((detail._meta.app_label, detail._meta.object_name))
		try:
			item.rate = rateplan.rating_set.get(implementation=implementation,
							chargeType=chargeType)
		except rateplan.rating_set.model.DoesNotExist:
			raise DeferRecord("%s has no rating for %s(%s)" % (item.consumer.account,
									implementation,
									chargeType))
		if callable(detail.charge):
			charge = detail.charge(item.rate)
		else:
			charge = detail.charge

		for attrname in ('chargedUnits', 'chargeableUnits'):
			attr = _getattr(detail, attrname)
			setattr(item, attrname, attr)

		item.charge = charge * Currency.objects.quote(item.consumer.account.currency,
								chargeCurrency, item.chargeTime)

		item.save(sync = sync)
		
		return item

class ItemRecord(models.Model):
	class Admin:
		list_display = ('chargeTime', 'rate', 'consumer', 'chargeDescription', 'charge')
		list_display_links = ('chargeDescription',)
		list_filter = ('rate',)
		search_fields = ('chargeDescription',)
		date_hierarchy = 'chargeTime'
	class Meta:
		ordering = ('-chargeTime',)
		get_latest_by = 'chargeTime'
		verbose_name = _('Billable Item')
		verbose_name_plural = _('Billable Items')
	__module__ = 'django.contrib.billing.models'
	hexdigest = models.CharField(maxlength=40)
	consumer = models.ForeignKey(Consumer, verbose_name = _('Consumer'))
	receipt = models.ForeignKey(Receipt)
	rate = models.ForeignKey(Rating)
	charge = models.DecimalField(max_digits=16, decimal_places=4, default="0.0", verbose_name = _('Charge'))
	chargeTime = models.DateTimeField(verbose_name = _('Time'))
	chargeableUnits = models.IntegerField(default = 1, verbose_name = _('Chargeable Units'))
	chargedUnits = models.IntegerField(default = 1, verbose_name = _('Charged Units'))
	chargeDescription = models.CharField(blank=True, maxlength=256, verbose_name = _('Description'))
	objects = ItemRecordManager()

	def detail(self):
		if not self.id:
			self.save()
		detail = self.rate.get(hexdigest = self.hexdigest)
		while True:
			if hasattr(detail, 'detail'):
				detail = getattr(detail, 'detail')
			elif callable(detail):
				detail = detail()
			else:
				break
		return detail

	def save(self, sync = True):
		if not self.id:
			try:
				self.receipt
			except Receipt.DoesNotExist:
				self.receipt = self.consumer.account.receiptForMonth(self.chargeTime)
		if self.receipt.issued:
			raise self.receipt.AlreadyIssued
		super(ItemRecord, self).save()
		if sync:
			self.receipt._refresh()

	def delete(self, sync = True):
		if self.receipt.issued:
			raise self.receipt.AlreadyIssued
		for detail in self.details():
			detail.unrecord()
		receipt = self.receipt
		super(ItemRecord, self).delete()
		if sync:
			receipt._refresh()

	def __str__(self):
		return '%s @ %.02f' % (self.chargeDescription, self.charge,)
