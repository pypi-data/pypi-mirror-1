#############################################################################
#                                                                           #
#    Copyright (C) 2006, 2007 William Waites <ww@styx.org>                  #
#    Copyright (C) 2006, 2007 Dmytri Kleiner <dk@haagenti.com>              #
#    Copyright (C) 2006, 2007 Haagenti Group Inc.                           #
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
#                                                                           #
#############################################################################

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.forex.models import Currency
from django.contrib.billing.utilities import pFloat
from django.conf import settings
from rate import RatePlan

__all__ = ['Account', 'Consumer']

class Account(models.Model):
	__module__ = 'django.contrib.billing.models'
	class Admin:
		list_display = ['created', 'description', 'memo', 'balance', 'currency', 'open']
		list_display_links = ['description']
		list_filter = ['open']
		search_fields = ['description', 'memo', 'contact']
	class Meta:
		ordering = ['description', 'created']
	description = models.CharField(maxlength=64, verbose_name = _('Description'),
					help_text=_("""
The name of the account as it should normally appear in lists, on invoices &c.
"""))
	created = models.DateTimeField(auto_now_add=True, verbose_name = _('Created'))
	contact = models.TextField(maxlength=1024, blank=True, verbose_name = _('Contact'),
				help_text=_("""
Contact information, street address, &c as should appear on invoices.
"""))
	memo = models.TextField(maxlength=1024, blank=True, verbose_name = _('Memo'),
				help_text=_("""
Optional descriptive text for internal consumption.
"""))
	rateplan = models.ForeignKey(RatePlan, blank=True, verbose_name = _('Rate Plan'),
				help_text=_("""
Rate plan for this account.
"""))
	currency = models.ForeignKey(Currency, default=settings.DEFAULT_CURRENCY,
				help_text=_("""
Currency in which charges to this account should be billed.
"""))
	open = models.BooleanField(default=True, verbose_name = _('Open'),
				help_text=_("""
Status of this account. Accounts can be sorted and filtered by this flag
on some screens.
"""))
	limited = models.BooleanField(default=True,
				help_text=_("""
This should be checked if the account is subject to credit limits. This is
used for prepaid applications.
"""))	
	creditlimit = models.DecimalField(max_digits=16, decimal_places=4, default="0.0",
				help_text=("""
If the above is checked, the relevant credit limit.
"""))

	def currentReceipt(self):
		from datetime import datetime
		return self.receiptForMonth(datetome.now())

	def receiptForMonth(self, stamp):
		from receipt import Receipt
		from datetime import date
		month = date(stamp.year, stamp.month, 1)
		Q = models.Q
		receipt_set = self.receipt_set.filter(Q(date__gt = month) | Q(date = month))
		if receipt_set.filter(issued__isnull = True).count():
			receipt = receipt_set.filter(issued__isnull = True).order_by("date")[0]
		elif receipt_set.count():
			last = receipt_set.latest("date")
			if last.date.month == 12: dtup = (last.date.year + 1, 1, 1)
			else: dtup = (last.date.year, last.date.month + 1, 1)
			month = date(*dtup)
			receipt = Receipt.objects.create(account = self, date = month)
		else:
			receipt = Receipt.objects.create(account = self, date = month)
		return receipt

	def defaultConsumer(self):
		from django.template.defaultfilters import slugify
		if not hasattr(self, '__defaultConsumer__'):
			number = slugify('%06d-' % self.id + self.description[:17]).upper()
			consumer, created = Consumer.objects.get_or_create(number = number, account = self)
			if created:
				print "%s created %s" % (self.__class__, consumer)
			setattr(self, '__defaultConsumer__', consumer)
		else:
			consumer = getattr(self, '__defaultConsumer__')
		return consumer
	
	def save(self):
		if not self.id:
			new = True
			try:
				self.currency
			except Currency.DoesNotExist:
				self.currency = Currency.objects.default()

			if not hasattr(settings, 'DEFAULT_CREDITLIMIT') or \
					settings.DEFAULT_CREDITLIMIT is None:
				self.limited = False
			elif settings.DEFAULT_CREDITLIMIT:
				self.creditlimit = settings.DEFAULT_CREDITLIMIT
		else:
			new = False
			original = Account.objects.get(id__exact=self.id)
			self.currency = original.currency

		if not self.rateplan_id:
			self.rateplan = RatePlan.objects.default(name = self.description)

		super(Account, self).save()

		if new and settings.AUTH_PROFILE_MODULE:
			from django.contrib.auth.models import User
			for u in User.objects.filter(is_staff = True):
				profile = u.get_profile()
				profile.accounts.add(self)

	def delete(self):
		if not self._meta.get_all_related_objects():
			super(Account, self).delete()
					
	def __str__(self):
		return self.description

	def balance(self):
		from django.db import connection
		cursor = connection.cursor()
		cursor.execute("""
		SELECT SUM(charge) FROM billing_receipt JOIN
			billing_itemrecord ON billing_receipt.id = receipt_id
		WHERE account_id = %d;
		""" % (self.id,))
		result = cursor.fetchall()
		cursor.close()
		if not result or not result[0] or not result[0][0]: return pFloat("0.0")
		else: return pFloat(result[0][0])
	balance.short_description = _('Balance')

	def available(self):
		return self.balance() + self.creditlimit
	
class Consumer(models.Model):
	__module__ = 'django.contrib.billing.models'
	class Admin:
		search_fields = ['number',]
		list_display = ['number', 'description']
		list_filter = ['account',]
	class Meta:
		ordering = ['number']
	number = models.SlugField(maxlength=64, unique=True)
	description = models.CharField(maxlength=64, blank=True)
	memo = models.CharField(maxlength=64, blank=True)
	account = models.ForeignKey(Account, blank=True)

	def save(self):
		try:
			self.account
		except Account.DoesNotExist:
			a = Account(description = '#' + self.number)
			a.save()
			self.account = a
		super(Consumer, self).save()
	def delete(self):
		if not self._meta.get_all_related_objects():
			super(Consumer, self).delete()
	def __str__(self):
		return self.number
