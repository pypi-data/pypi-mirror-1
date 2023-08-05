#############################################################################
#                                                                           #
#    Copyright (C) 2007 William Waites <ww@styx.org>                        #
#                                                                           #
#    This program is free software; you can redistribute it and/or modify   #
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
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models.loading import get_model

from billable import get_billables, Billables

__all__ = ['RatePlan', 'Rating']

if not hasattr(settings, 'DEFAULT_RATEPLAN_ID'):
	settings.DEFAULT_RATEPLAN_ID = None
if not hasattr(settings, 'DEFAULT_RATEPLAN_COPY'):
	settings.DEFAULT_RATEPLAN_COPY = False
if not hasattr(settings, 'RATEPLAN_POPULATE'):
	settings.RATEPLAN_POPULATE = True

class RatePlanManager(models.Manager):
	def default(self, *av, **kw):
		if settings.DEFAULT_RATEPLAN_ID:
			default_rateplan = self.get(pk = settings.DEFAULT_RATEPLAN_ID)
		if settings.DEFAULT_RATEPLAN_COPY:	
			rateplan = default_rateplan.copy()
			rateplan.name = kw.get('name', 'Rate Plan')
			rateplan.save()
		elif settings.DEFAULT_RATEPLAN_ID:
			rateplan = default_rateplan
		else:
			rateplan = self.create(*av, **kw)
			if settings.RATEPLAN_POPULATE:
				rateplan.populate()
		return rateplan

class RatePlan(models.Model):
	__module__ = 'django.contrib.billing.models'
	class Admin:
		list_display = ('name', 'description')
	class Meta:
		verbose_name = _('Rate Plan')
		verbose_name_plural = _('Rate Plans')
	objects = RatePlanManager()
	name = models.CharField(maxlength = 64, verbose_name = _('Name'))
	description = models.TextField(maxlength = 1024, verbose_name = _('Description'))
	def __str__(self):
		return self.name
	def get_or_create(self, **kw):
		return Rating.objects.get_or_create(ratePlan = self, **kw)
	def copy(self):
		new = RatePlan.objects.create(name = self.name, description = 'Copy of %08d' % (self.id,))
		for rate in self.rating_set.all():
			try:
				new_rate = new.rating_set.get(implementation = rate.implementation,
								chargeType = rate.chargeType)
			except new.rating_set.model.DoesNotExist:
				new_rate = Rating(ratePlan = new,
						implementation = rate.implementation,
						chargeType = rate.chargeType)
			new_rate.chargeDescription = rate.chargeDescription
			new_rate.amount = rate.amount
			new_rate.minChargeUnits = rate.minChargeUnits
			new_rate.chargeIncrement = rate.chargeIncrement

			new_rate.save()
		return new
	def populate(self):
		for billable in get_billables():
			implementation = '.'.join((billable._meta.app_label, billable._meta.object_name))
			if hasattr(billable._meta.billing, 'chargeDefaults'):
				for chargeType in billable._meta.billing.chargeDefaults:
					self.get_or_create(implementation = implementation,
							chargeType = chargeType)
	
class Rating(models.Model):
	__module__ = 'django.contrib.billing.models'
	ratePlan = models.ForeignKey(RatePlan, edit_inline = True)
	implementation = models.CharField(maxlength = 256, choices = Billables(), core = True,
				verbose_name = _('Rated Item'))
	chargeType = models.CharField(maxlength = 16, verbose_name = _('Charge Type'), default = '0000')
	chargeDescription = models.CharField(maxlength = 64, verbose_name = _('Description'), default = '')
	amount = models.DecimalField(max_digits=16, decimal_places=4, verbose_name = _('Amount'),
				help_text = """
Fixed amount, duration based amount or decimal percentage
according to the type of charge.
""")
	minChargeUnits = models.IntegerField(verbose_name = _('Minimum Charged Units'), default = 1)
	chargeIncrement = models.IntegerField(verbose_name = _('Charging Increments'), default = 1)
	def __str__(self):
		return "%s (%s)" % (self.get_model()._meta.verbose_name, self.chargeType)

	def save(self):
		if not self.amount or not self.chargeDescription:
			opts = self.get_model()._meta.billing
			if self.chargeType not in opts.chargeDefaults:
				raise AttributeError("%s: could not determine amount" % (self,))
			amount, chargeDescription = opts.chargeDefaults[self.chargeType]
			if not self.amount:
				self.amount = amount
			if not self.chargeDescription:
				self.chargeDescription = str(chargeDescription)
		super(Rating, self).save()
		
	def get_model(self):
		app_label, object_name = self.implementation.split('.')
		return get_model(app_label, object_name)

	def get(self, *av, **kw):
		model = self.get_model()
		return model._default_manager.get(*av, **kw)

	def delete(self):
		if self.itemrecord_set.count():
			raise IntegrityError("Cannot delete Rate")
		super(Rating, self).delete()

	def description(self):
		return self.get_model()._meta.verbose_name
	description.short_description = _('Description')

	def doc(self):
		return self.get_model().__doc__
