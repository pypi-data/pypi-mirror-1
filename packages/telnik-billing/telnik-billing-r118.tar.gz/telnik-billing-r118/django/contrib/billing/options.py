#############################################################################
#                                                                           #
#    Copyright (C) 2006, 2007 William Waites <ww@styx.org>                  #
#    Copyright (C) 2006, 2007 Dmytri Kleiner <dk@trick.ca>                  #
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

from django.contrib.options import MetaOptions
class BillingOptions(MetaOptions):
	def _contribute_to_class(opt, cls, name):
		from django.db.models import CharField, DateTimeField
		from django.conf import settings
		from django.utils.translation import gettext_lazy as _
		from django.contrib.forex.models import Currency
		from django.contrib.billing.models import Billable

		options = MetaOptions._contribute_to_class(opt, cls, name)

		opt.setdefault(cls, options, 'hexdigest',
				CharField(maxlength=40, unique=True, verbose_name=_('Hex Digest'), editable=False))
		opt.setdefault(cls, options, 'charge', lambda self, rate: rate.amount)
		opt.setdefault(cls, options, 'chargeCurrency', settings.DEFAULT_CURRENCY)
		opt.setdefault(cls, options, 'chargeTime',
				DateTimeField(auto_now_add = True, verbose_name = _('Charge Time')))
		opt.setdefault(cls, options, 'chargeType', '0000')
		opt.setdefault(cls, options, 'chargedUnits', 1)
		opt.setdefault(cls, options, 'chargeableUnits', 1)
		opt.setdefault(cls, options, 'chargeDescription', cls._meta.verbose_name)
		opt.setdefault(cls, options, 'chargeDefaults', {})
		cls.add_to_class('item', Billable.item)
		cls.add_to_class('save', Billable.save)
		cls.add_to_class('rehash', Billable.rehash)
		cls.add_to_class('update', Billable.update)
		return options
	
	contribute_to_class = classmethod(_contribute_to_class)
	_contribute_to_class = staticmethod(_contribute_to_class)
