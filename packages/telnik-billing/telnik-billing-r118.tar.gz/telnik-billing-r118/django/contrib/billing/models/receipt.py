from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from decimal import Decimal
from account import Account

__all__ = ['Receipt']

class Receipt(models.Model):
	__module__ = 'django.contrib.billing.models'
	class Admin:
		search_fields = ('number', 'memo')
		list_display = ('number', 'account', 'date', 'amount')
		list_filter = ('account',)
		date_hierarchy = 'date'
	class Meta:
		ordering = ['-date', 'account', 'number']
		get_latest_by = 'date'
		unique_together = (('account','number'),)
		verbose_name = _('Invoice')
		verbose_name_plural = 'Invoices'
	class AlreadyIssued(Exception): pass
	account = models.ForeignKey(Account, verbose_name = _('Account'))
	number = models.CharField(verbose_name = _('Number'), maxlength=32, blank=True)
	memo = models.CharField(verbose_name = _('Memo'), maxlength=256, blank=True)
	created = models.DateField(verbose_name = _('Created'), auto_now_add=True)
	date = models.DateField(verbose_name = _('Date'), blank=True, null=True)	
	updated = models.DateField(verbose_name = _('Updated'), auto_now_add=True)
	issued =  models.DateField(verbose_name = _('Issued'), blank=True, null=True)
	amount = models.DecimalField(max_digits=16, decimal_places=4, verbose_name = _('Amount'), blank=True, default="0.0")
	def total(self):
		return self.amount
	def _refresh(self):
		from django.db import connection
		cursor = connection.cursor()
		cursor.execute("""
		SELECT
			round(sum(charge),3) as total
		FROM
			billing_itemrecord
		WHERE
			billing_itemrecord.receipt_id = %s
		""", [self.id])
		row = cursor.fetchone()
		value = row[0]
		if not value:
			value = Decimal('0.0')
		self.amount = value
		super(self.__class__, self).save()

	def opening(self):
		from django.db import connection
		cursor = connection.cursor()
		cursor.execute("""
		SELECT SUM(amount) FROM billing_receipt
		WHERE account_id = %d AND billing_receipt.date < '%s';
		""" % (self.account.id, self.date))
		result = cursor.fetchall()
		cursor.close()
		if not result or not result[0] or not result[0][0]:
			return Decimal("0.0")
		else:
			return result[0][0]
	def closing(self):
		return self.opening() + self.total()
	def json_total(self):
		return self.total()
	def isIssued(self):
		return self.issued and True
	isIssued.boolean = True

	def summary(self):
		from django.db import connection
		cursor = connection.cursor()
		cursor.execute("""
		SELECT billing_rating.id, sum("chargedUnits") AS count, sum(charge) AS total
		FROM billing_itemrecord JOIN billing_rating ON billing_itemrecord.rate_id = billing_rating.id
		WHERE billing_itemrecord.receipt_id = %d AND billing_itemrecord.charge != 0
		GROUP BY billing_rating.id, billing_rating.implementation
		ORDER BY billing_rating.implementation, total DESC;
		""" % (self.id,))
		result = cursor.fetchone()
		while result:
			rate_id, count, total = result
			rate = self.account.rateplan.rating_set.get(pk = rate_id)
			yield rate, count, total
			result = cursor.fetchone()
		cursor.close()
		
	def save(self):
		if self.id:
			saved = Receipt.objects.get(id__exact = self.id)
			if self.issued:
				if saved.issued:
					raise self.AlreadyIssued("Invoice already issued.")

		if not self.number:
			self.number = "..."
			super(Receipt, self).save()
			if hasattr(settings, 'RECIEPT_PREFIX'):
				prefix = settings.RECIEPT_PREFIX
			else:
				prefix = 'INVOICE'
			self.number = "%s%04d%02d-%08d" % (prefix, self.date.year,
							self.date.month, self.id)
		super(Receipt, self).save()

	def delete(self):
		if not self.itemrecord_set.all().count():
			pass

	def update(self, when = None):
		from datetime import datetime
		if not when:
			self.updated = datetime.now()
		else:
			self.updated = when
		super(Receipt, self).save()
		
		
	def __str__(self):
		return self.number
