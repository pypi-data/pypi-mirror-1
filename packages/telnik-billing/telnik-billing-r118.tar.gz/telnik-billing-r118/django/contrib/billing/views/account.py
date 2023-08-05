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
from django.db.models import Q
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import cache_page
from django.contrib.billing.models import Account, Consumer, ItemRecord
from django import newforms as forms

def account_for_request(request, account_id):
	try:
		return request.user.get_profile().accounts.get(pk = account_id)
	except Account.DoesNotExist:
		raise Http404
	
def account_extra(request):
	profile = request.user.get_profile()
	where = [
		"billing_account.id IN (SELECT %s FROM %s WHERE %s = %s)" % (
			profile.accounts.target_col_name,
			profile.accounts.join_table,
			profile.accounts.source_col_name,
			profile.id),
	]
	return { 'where' : where }

class AccountChangeList(ChangeList):
	def __init__(self, request, model):
		self.request = request
		super(AccountChangeList, self).__init__(request, model)
	def get_query_set(self):
		query_set = super(AccountChangeList, self).get_query_set()
		return query_set.extra(**account_extra(self.request))

@staff_member_required
@cache_page
def account_list(request, template = 'account_list.html'):
	t = loader.get_template(template)
	c = RequestContext(request, { 'cl' : AccountChangeList(request, Account) })
	return HttpResponse(t.render(c))

@staff_member_required
def account_consumer(request, account_id, template = 'account_consumer.html'):
	account = account_for_request(request, account_id)
	class ConsumerChangeList(ChangeList):
		def get_query_set(self):
			query_set = super(ConsumerChangeList, self).get_query_set()
			return query_set.filter(account = account)
	t = loader.get_template(template)
	c = RequestContext(request, { 'account' : account, 'cl' : ConsumerChangeList(request, Consumer) })
	return HttpResponse(t.render(c))

@staff_member_required
def account_rateplan(request, account_id, template = 'account_rating.html'):
	account = account_for_request(request, account_id)
	t = loader.get_template(template)

	editable = request.user.has_perm('billing.admin_billing')
	rates = account.rateplan.rating_set.filter()

	if 'action' in request.POST and request.POST['action'] == 'saverate':
		try:
			manipulator = rates.model.ChangeManipulator(request.POST['id'])
		except rates.model.DoesNotExist:
			raise Http404
		new_data = request.POST.copy()
		errors = manipulator.get_validation_errors(new_data)
		if not errors:
			manipulator.save(new_data)
			message = "%s %s %s: %s" % (_("Updated rate on"),
						    manipulator.original_object.description(),
						    manipulator.original_object.chargeType,
						    manipulator.original_object.amount)
			request.user.message_set.create(message = message)
		else:
			request.user.message_set.create(message = str(errors))
			request.user.message_set.create(message = _("Error saving Rate. Bad input."))
	else:
		errors = {}

	context = {
		'account' : account,
		'rates' : rates,
		'editable' : editable,
		'errors' : errors,
	}
	c = RequestContext(request, context)
	return HttpResponse(t.render(c))

@staff_member_required
def consumer_charges(request, account_id, consumer_id, template = 'consumer_charges.html'):
	from receipt import ItemChangeList
	account = account_for_request(request, account_id)
	try: consumer = account.consumer_set.get(pk=consumer_id)
	except account.consumer_set.model.DoesNotExist:
		raise Http404
	class CItemChangeList(ItemChangeList):
		def get_query_set(self):
			self.manager = consumer.itemrecord_set
			return super(CItemChangeList, self).get_query_set()
	t = loader.get_template(template)
	c = RequestContext(request, {'account' : account,
								 'consumer' : consumer,
								 'cl' : CItemChangeList(consumer, request, ItemRecord) })
	return HttpResponse(t.render(c))
	
@staff_member_required
def account_add(request):
	accounts = request.user.get_profile().accounts.all()
	manipulator = accounts.model.AddManipulator()
	context = {
		'manipulator' : manipulator,
	}
	if request.method == "POST":
		new_data = request.POST.copy()
	        errors = manipulator.get_validation_errors(new_data)
		if errors:
			context['errors'] = errors
        	else:
			manipulator.do_html2python(new_data)
			account = manipulator.save(new_data)
			return HttpResponseRedirect('../')
	t = loader.get_template('account_add.html')
	c = RequestContext(request, context)
	return HttpResponse(t.render(c))

@staff_member_required
def account_edit(request, pk, template="account_edit.html"):
	account = account_for_request(request, pk)
	Form = forms.form_for_instance(account)
	if request.POST:
		f = Form(request.POST)
		try:
			f.save()
			return HttpResponseRedirect('../')
		except ValueError:
			pass
	else:
		f = Form()
	context = {
		'account' : account,
		'form' : f,
	}
	t = loader.get_template(template)
	c = RequestContext(request, context)
	return HttpResponse(t.render(c))

@staff_member_required
#@cache_page #(60 * 60)
def account_show(request, account_id, template = "account_receipt.html"):
	accounts = request.user.get_profile().accounts.all()
	try:
		account = accounts.get(pk = account_id)
	except accounts.model.DoesNotExist:
		raise Http404
	context = {
		'account' : account,
	}
	t = loader.get_template(template)
	c = RequestContext(request, context)
	return HttpResponse(t.render(c))

@staff_member_required
def current_receipt(request, account_id):
	from datetime import datetime
	accounts = request.user.get_profile().accounts.all()
	try:
		account = accounts.get(pk = account_id)
	except accounts.models.DoesNotExist:
		raise Http404
	receipt = account.receiptForMonth(datetime.now())
	return HttpResponseRedirect('/admin/billing/receipt/%d/' % (receipt.id,))

@staff_member_required
@cache_page
def account_stats(request):
	from django.contrib.billing.utilities import pFloat
	from datetime import datetime
	from Scientific.Statistics import average, mean, standardDeviation
	accounts = request.user.get_profile().accounts.filter(open__exact=True)
	now = datetime.now()
	date = '%04d-%02d-01' % (now.year, now.month)

	def latest_total(x):
		try:
			return float(x.receipt_set.filter(date__lt = date).latest().total())
		except x.receipt_set.model.DoesNotExist:
			return 0.0
	def current_total(x):
		try:
			return float(x.receipt_set.latest().total())
		except x.receipt_set.model.DoesNotExist:
			return 0.0

	context = {
		'now' : now,
		'stats' : [],
		'total' : sum(map(lambda x: float(x.balance()), accounts)),
		'last' : sum(map(lambda x: latest_total(x), accounts)),
		'todate' : sum(map(lambda x: current_total(x), accounts)),
	}
	for a in accounts.order_by('description'):
		try:
			s = { 'account' : a }
			s['receipts'] = a.receipt_set.filter(date__lt = date)
			s['current'] = a.receipt_set.latest()
			s['latest'] = s['receipts'].latest()
			s['totals'] = map(lambda x: float(x.total()), s['receipts'])
			s['min'] = min(s['totals'])
			s['max'] = max(s['totals'])
			s['average'] = average(s['totals'])
			s['dev'] = float(s['latest'].total()) - s['average']
			try: ## sometimes gives div by zero error FIXME
				s['stddev'] = standardDeviation(s['totals'])
			except: s['stddev'] = 0
			if s['latest'].total() and abs(s['dev']) > s['stddev']:
				s['flag'] = True
			else:
				s['flag'] = False
			context['stats'].append(s)
		except a.receipt_set.model.DoesNotExist:
			pass
	t = loader.get_template('account_stats.html')
	c = RequestContext(request, context)
	return HttpResponse(t.render(c))

