from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.options import MetaOptions
from django.contrib.billing.options import BillingOptions
from django.contrib.billing.models.receipt import Receipt
from datetime import datetime

__all__ = ['Charge']

genericChargeDefaults = {
	'C' : (0, _('Correction')),
	'S' : (0, _('Support')),
	'R' : (0, _('Periodic Charge')),
}

class GenericChargeChoices:
	def __iter__(self):
		from django.db import connection
		for k in genericChargeDefaults:
			yield k, genericChargeDefaults[k][1]
		cursor = connection.cursor()
		try:
			cursor.execute("""
SELECT DISTINCT "chargeType", "chargeDescription" FROM billing_rating
WHERE implementation = 'django.contrib.billing.models.Charge'
GROUP BY "chargeType", "chargeDescription"
ORDER BY "chargeType";
			""")
		except:
			## is this really safe?
			connection._rollback()
			return
		while True:
			try:
				chargeType, chargeDescription = cursor.fetchone()
				if chargeType in genericChargeDefaults:
					continue
				yield chargeType, chargeDescription
			except:
				break

class Charge(models.Model):
	__module__ = 'django.contrib.billing.models'
	class Admin:
		list_display = ('chargeTime', 'receipt', 'chargeType', 'chargedUnits', 'chargeableUnits')
		list_display_links = ('chargeType',)
		search_fields = ('chargeDescription',)
		date_hierarchy = 'chargeTime'
	class Meta:
		verbose_name = _('Charge')
		verbose_name_plural = _('Generic Charges')
	class Billing(BillingOptions):
		dataType = 'TELNIK_BILLING_CHARGE'
		dataKeys = ('receipt__number', 'unique')
		chargeDefaults = genericChargeDefaults
	class CSV(MetaOptions):
		separator = ';'
		format = (
			('chargeType', _('Type')),
			('chargeDescription', _('Description')),
			('chargeableUnits', _('Units')),
			('chargedRate', _('Charge')),
		)
	receipt = models.ForeignKey(Receipt)
	chargeType = models.CharField(maxlength = 16, choices = GenericChargeChoices(), verbose_name = _('Charge Type'))
	chargeDescription = models.TextField(maxlength = 1024, verbose_name = _('Description'))
	chargeableUnits = models.IntegerField(verbose_name = _('Chargeable Units'), default = 1)
	chargedRate = models.DecimalField(max_digits=16, decimal_places=4, verbose_name = _('Rate / Unit'))
	def charge(self, rate):
		return rate.amount * self.chargeableUnits
	def chargedUnits(self):
		return self.chargeableUnits
	def chargeCurrency(self):
		return self.receipt.account.currency
	def unique(self):
		return datetime.now()
	def consumer(self):
		implementation = '.'.join((self._meta.app_label, self._meta.object_name))
		rate, created = self.receipt.account.rateplan.get_or_create(implementation = implementation, chargeType = self.chargeType)
		return self.receipt.account.defaultConsumer()
