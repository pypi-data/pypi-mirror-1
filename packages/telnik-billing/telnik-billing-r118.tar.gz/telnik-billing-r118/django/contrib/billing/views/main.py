#############################################################################
#                                                                           #
#    Copyright (C) 2007 William Waites <ww@styx.org>                        #
#    Copyright (C) 2007 Dmytri Kleiner <dk@haagenti.com>                    #
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
#                                                                           #
#############################################################################

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models.loading import get_model

@login_required
def hello(request, template = 'hello.html'):
	t = loader.get_template(template)
	sections = [
		{ 'href': 'account/', 'text': 'Accounts'},
		{ 'href': 'receipt/', 'text': 'Invoices'},
	]
	if request.user.is_staff:
		sections.append({ 'href': 'account/stats/', 'text': 'Statistics'})
	c = RequestContext(request, {'sections': sections})
	return HttpResponse(t.render(c))

@login_required
def trafficbymonth(request):
	from django.db import connection
	cursor = connection.cursor()
	cursor.execute("""
	SELECT
		billing_rating.implementation,
		billing_receipt.date,
		count(*) as volume
	FROM
		billing_itemrecord JOIN billing_receipt ON
			billing_itemrecord.receipt_id = billing_receipt.id
			JOIN billing_account ON billing_receipt.account_id = billing_account.id
			JOIN billing_rateplan ON billing_account.rateplan_id = billing_rateplan.id
			JOIN billing_rating ON billing_rating."ratePlan_id" = billing_rateplan.id
	GROUP BY
		billing_rating.implementation, billing_receipt.date
	ORDER BY
		billing_receipt.date DESC, billing_rating.implementation
	""")
	class Dummy(object):
		def __init__(self, row):
			self.implementation = get_model(*row[0].split('.'))
			self.opts = self.implementation.meta
			self.date = '%04d-%02d-%02d' %(row[1].year, row[1].month, row[1].day)
			self.volume = row[2]

	qs = map(Dummy, cursor.fetchall())
	t = loader.get_template('trafficbymonth.html')
	c = RequestContext(request, {'traffic': qs})
	response = HttpResponse(t.render(c))
	return response

@login_required
def trafficformonth(request, handler, date):
	from django.db import connection
	cursor = connection.cursor()
	cursor.execute("""
	SELECT
		billing_receipt.id,
		count(*) as volume
	FROM
		billing_itemrecord, billing_receipt, billing_account
	WHERE
		billing_itemrecord.receipt_id = billing_receipt.id
		AND billing_receipt.account_id = billing_account.id
		AND billing_itemrecord.handler = '%s'
		AND billing_receipt.date = '%s'
	GROUP BY
		billing_receipt.id, billing_receipt.number, billing_account.description
	""" % (handler, date))

	class Dummy(object):
		def __init__(self, row):
			self.receipt = Receipt.objects.get(id__exact = row[0])
			self.volume = row[1]
	qs = map(Dummy, cursor.fetchall())
	t = loader.get_template('trafficformonth.html')
	c =Context({'traffic': qs, 'handler':handler, 'date':date})
	response = HttpResponse(t.render(c))
	return response
