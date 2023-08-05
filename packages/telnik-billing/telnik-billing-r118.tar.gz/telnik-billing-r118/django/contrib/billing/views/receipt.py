from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext, Context
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import Permission
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.filterspecs import FilterSpec
from django.db.transaction import commit_on_success
from django.contrib.billing.models import Receipt, ItemRecord
from datetime import datetime 
from account import account_extra

__all__ = ['receipt_list', 'receipt_issue', 'receipt_view', 'receipt_pdf', 'receipt_detail', 'charge_add', 'charge_show', 'receipt_for_request']

def receipt_for_request(request, receipt_id):
	try:
		return Receipt.objects.filter().extra(**receipt_extra(request)).get(pk = receipt_id)
	except Receipt.DoesNotExist:
		raise Http404

def receipt_extra(request):
	profile = request.user.get_profile()
	where = "account_id IN (SELECT %s FROM %s WHERE %s = %s)" % (
		profile.accounts.target_col_name,
		profile.accounts.join_table,
		profile.accounts.source_col_name,
		profile.id)
	return { 'where' : [where] }

class ReceiptChangeList(ChangeList):
	def __init__(self, request, model):
		self.request = request
		super(ReceiptChangeList, self).__init__(request, model)
	def total(self):
		return sum(map(lambda x: x.total(), self.query_set))
	def get_query_set(self):
		query_set = super(ReceiptChangeList, self).get_query_set()
		return query_set.extra(**receipt_extra(self.request))
	def get_filters(self, request):
		filter_specs = []
		if self.lookup_opts.admin.list_filter and not self.opts.one_to_one_field:
			filter_fields = [self.lookup_opts.get_field(field_name) \
							  for field_name in self.lookup_opts.admin.list_filter]
			for f in filter_fields:
				spec = FilterSpec.create(f, request, self.params, self.model)
				spec.lookup_choices = spec.lookup_choices.extra(**account_extra(self.request))
				if spec and spec.has_output():
					filter_specs.append(spec)
		return filter_specs, bool(filter_specs)

class ItemChangeList(ChangeList):
	def __init__(self, receipt, request, model):
		self.receipt = receipt
		self.account = receipt.account
		self.request = request
		super(ItemChangeList, self).__init__(request, model)
   	def get_query_set(self):
	   	self.manager = self.receipt.itemrecord_set
		query_set = super(ItemChangeList, self).get_query_set()
		return query_set.filter(chargedUnits__gt=0)
	def get_filters(self, request):
		filter_specs = []
		if self.lookup_opts.admin.list_filter and not self.opts.one_to_one_field:
			filter_fields = [self.lookup_opts.get_field(field_name) \
							  for field_name in self.lookup_opts.admin.list_filter]
			for f in filter_fields:
				spec = FilterSpec.create(f, request, self.params, self.model)
				spec.lookup_choices = self.account.rateplan.rating_set.all()
				if spec and spec.has_output():
					filter_specs.append(spec)
		return filter_specs, bool(filter_specs)
	def url_for_result(self, item):
		return "/admin/billing/receipt/%s/charges/%s/" % (item.receipt.id, item.hexdigest,)

@staff_member_required
def receipt_list(request, template = 'receipt_list.html'):
	t = loader.get_template(template)
	c = RequestContext(request, { 'cl' : ReceiptChangeList(request, Receipt) })
	return HttpResponse(t.render(c))

def receipt_render(request, receipt_id, template = 'receipt_view.html'):
	from os import system
	from decimal import Decimal
	from django.contrib.billing.models import get_billables
	receipt = receipt_for_request(request, receipt_id)
	details = []
	seen_rates = []

	if 'action' in request.POST:
		if request.POST['action'] == 'rerate':
			try:
				rate = receipt.account.rateplan.rating_set.get(pk = request.POST['rating_id'])
				rate.amount = Decimal(request.POST['amount'])
				rate.save()
			except:
				raise Http404
			cmd = "/usr/bin/billing_rerate %s %d %d &" % (request.user.username, receipt.id, rate.id)
			message = "%s: %s @ %.04f" % (_('Rate recalculation'), rate.chargeDescription, rate.amount)
			request.user.message_set.create(message = message)
			system(cmd)

	for rate, count, total in receipt.summary():
		if rate.implementation not in seen_rates:
			seen_rates.append(rate.implementation)
			csv_href = '%d/csv/' % (rate.id,)
		else:
			csv_href = None
		detail = {
			'rating_id' : rate.id,
			'description' : rate.get_model()._meta.verbose_name,
			'chargeType' : rate.chargeType,
			'implementation' : rate.implementation,
			'price' : rate.amount,
			'count' : count,
			'total' : total,
			'csv_href' : csv_href,
		}
		details.append(detail)

	context = { 'opts' : Receipt._meta,
		  'receipt' : receipt,
		  'change' : False,
		  'details' : details,
		  'is_popup' : False,
		  'has_delete_permission' : False,
		  'has_change_permission' : False,
		  'has_add_permission' : False,
		  'editable' : request.user.has_perm('billing.admin_billing') and not receipt.issued,
	}

	t = loader.get_template(template)
	return t.render(RequestContext(request, context))

@staff_member_required
def receipt_view(request, receipt_id, **kw):
	data = receipt_render(request, receipt_id, **kw)
	return HttpResponse(data)

@staff_member_required
def receipt_pdf(request, receipt_id, template = 'invoice.html'):
	import tempfile, os
	receipt = receipt_for_request(request, receipt_id)
	data = receipt_render(request, receipt_id, template)
	htmlfile = tempfile.mktemp()
	pdffile = tempfile.mktemp()
	file = open(htmlfile, "w")
	file.write(data)
	file.close()
	cmdline = "/usr/bin/htmldoc --quiet --webpage -t pdf %s -f %s" % (htmlfile, pdffile)
	cmd = os.popen(cmdline)
	cmd.close()
	os.remove(htmlfile)

	file = open(pdffile, "r")

	response = HttpResponse(mimetype='application/pdf')
	response['Content-Disposition'] = "attachment; filename=%s.pdf" % (receipt.number,)

	response.write(file.read())
	file.close()
	os.remove(pdffile)

	return response

@staff_member_required
def receipt_detail(request, receipt_id, template = 'receipt_detail.html'):
	from django.contrib.billing.models import ItemRecord
	receipt = receipt_for_request(request, receipt_id)
	t = loader.get_template(template)
	c = RequestContext(request, { 'receipt' : receipt, 'cl' : ItemChangeList(receipt, request, ItemRecord) })
	return HttpResponse(t.render(c))

@staff_member_required
@commit_on_success
def charge_add(request, receipt_id, template = 'charge_add.html'):
	from django.contrib.billing.models import Charge
	manipulator = Charge.AddManipulator()
	receipt = receipt_for_request(request, receipt_id)
	context = {
		'receipt' : receipt,
		'manipulator' : manipulator,
	}
	if request.method == "POST":
		new_data = request.POST.copy()
		errors = manipulator.get_validation_errors(new_data)
		if errors:
			context['errors'] = errors
		else:
			manipulator.do_html2python(new_data)
			charge = manipulator.save(new_data)
			item, created = ItemRecord.objects.get_or_create(charge)
			request.user.message_set.create(message = "Added %s to %s" % (item, receipt))
			return HttpResponseRedirect('../charges/')
	t = loader.get_template(template)
	c = RequestContext(request, context)
	return HttpResponse(t.render(c))

@staff_member_required
@commit_on_success
def charge_show(request, receipt_id, charge_id, template = 'charge_show.html'):
	from django.contrib.billing.models import Charge
	from django.contrib.billing.utilities import getattr_anyhow
	manipulator = Charge.AddManipulator()
	receipt = receipt_for_request(request, receipt_id)
	try:
		item = receipt.itemrecord_set.get(hexdigest = charge_id)
	except receipt.itemrecord_set.model.DoesNotExist:
		raise Http404
	context = {
		'receipt' : receipt,
		'charge' : item,
	}
	if request.user.is_superuser or request.user.is_staff or request.user.has_perm('admin.billing'):
		implementation = '.'.join((detail._meta.app_label, detail._meta.object_name))
		context['has_admin_billing'] = True
		detail = item.detail()
		context['detail_type'] = detail._meta.verbose_name
		context['detail_implementation'] = implementation
		context['detail_fields'] = []
		if hasattr(detail._meta.billing, 'detailDisplay'):
			for field, descr in detail._meta.billing.detailDisplay:
				context['detail_fields'].append((descr, getattr_anyhow(detail, field)))
	t = loader.get_template(template)
	c = RequestContext(request, context)
	return HttpResponse(t.render(c))

@staff_member_required
@commit_on_success
def receipt_issue(request, pk, template = 'receipt_issue.html'):
	receipt = receipt_for_request(request, pk)

	if 'issue' in request.POST:
		receipt._refresh()
		receipt.issued = datetime.now()
		receipt.save()
		return HttpResponseRedirect('../')

	context = {
		'receipt' : receipt,
	}
	t = loader.get_template(template)
	c = RequestContext(request, context)
	return HttpResponse(t.render(c))
