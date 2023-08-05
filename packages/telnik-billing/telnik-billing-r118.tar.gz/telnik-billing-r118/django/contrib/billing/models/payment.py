from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.options import MetaOptions
from django.contrib.billing.options import BillingOptions
from django.contrib.billing.models.receipt import Account
from django.contrib.forex.models import Currency
from django.contrib.auth.models import User
from django.conf import settings

__all__ = ['Payment']

class Payment(models.Model):
	__module__ = 'django.contrib.billing.models'
	class Admin:
		list_display = ('chargeTime', 'user', 'account', 'chargeReference', 'chargeMemo', 'chargeAmount')
		list_display_links = ('chargeReference',)
		search_fields = ('chargeReference', 'chargeMemo')
		date_hierarchy = 'chargeTime'
	class Meta:
		verbose_name = _('Payment')
		verbose_name_plural = _('Payments')
	class Billing(BillingOptions):
		dataType = 'TELNIK_BILLING_PAYMENT'
		dataKeys = ('account__id', 'chargeTime', 'chargeAmount', 'chargeReference')
		chargeDefaults = { 'X' : (0, _('Payment')) }
	class CSV(MetaOptions):
		separator = ';'
		format = (
			('chargeTime', _('Time')),
			('account', _('Account')),
			('chargeReference', _('Reference')),
			('chargeMemo', _('Memo')),
			('chargeAmount', _('Charge')),
		)
	account = models.ForeignKey(Account, editable=False, verbose_name = _('Account'))
	user = models.ForeignKey(User, editable=False, verbose_name = _('User'))
	chargeAmount = models.DecimalField(max_digits=16, decimal_places=4, verbose_name = _('Amount'))
	chargeCurrency = models.ForeignKey(Currency, default=settings.DEFAULT_CURRENCY, verbose_name = _('Currency'))
	chargeReference = models.CharField(maxlength=32, verbose_name = _('Reference'),
				help_text=_("""
A reference number (such as a bank transaction ID or cheque number)
identifying this transaction.
"""))
	chargeMemo = models.CharField(maxlength=64, blank=True, null=True, verbose_name = _('Memo'),
				help_text=_("""
An optional descriptive text for this payment.
"""))
	def charge(self, rate):
		return -1 * self.chargeAmount
	@property
	def chargeType(self):
		return 'X'
	def chargedUnits(self):
		return 1
	def chargeDescription(self):
		if self.chargeMemo:
			return ' '.join((self.chargeReference, self.chargeMemo))
		else:
			return self.chargeReference
	def consumer(self):
		implementation = '.'.join((self._meta.app_label, self._meta.object_name))
		rate, created = self.account.rateplan.get_or_create(implementation = implementation, chargeType = self.chargeType)
		return self.account.defaultConsumer()
