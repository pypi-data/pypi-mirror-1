from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.transaction import commit_on_success

__all__ = ['detail_csv']

@login_required
@commit_on_success
def detail_csv(request, receipt_id, rate_id):
	from django.contrib.options.csv import csv, Unimplemented
	from django.contrib.billing.models import ItemRecord
	from django.contrib.billing.views.receipt import receipt_for_request
	receipt = receipt_for_request(request, receipt_id)
	try:
		rate = receipt.account.rateplan.rating_set.get(pk = rate_id)
	except receipt.account.rateplan.rating_set.model.DoesNotExist:
		raise Http404
		
	model = rate.get_model()

	separator = model._meta.csv.separator
	format = model._meta.csv.format
	implementation = '.'.join((model._meta.app_label, model._meta.object_name))

	where = [
		'billing_itemrecord.receipt_id = %s' % receipt_id,
		'billing_itemrecord.rate_id = billing_rating.id',
		'billing_itemrecord.hexdigest = "%s".hexdigest' % model._meta.db_table,
		"billing_rating.implementation = '%s'" % implementation,
	]
	tables = ["billing_itemrecord", "billing_rating"]

	try:
		rows = csv(model, where = where, tables = tables)
	except Unimplemented:
		raise Http404('No CSV Implementation')

	response = HttpResponse(rows, mimetype="text/csv")
	response['Content-Disposition'] = "attachment; filename=%s-%s.csv" % (
			receipt.number,
			model._meta.object_name)
	return response
