from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.billing.models import ItemRecord, Payment, DetailAlreadyExists
from django.db.transaction import commit_on_success
from django.utils.translation import ugettext_lazy as _
from django import newforms as forms
from account import account_for_request

__all__ = ['payment_add']

@staff_member_required
@commit_on_success
def payment_add(request, account_id, template = 'payment_add.html'):
	account = account_for_request(request, account_id)
	Form = forms.form_for_model(Payment)
	if request.POST:
		f = Form(request.POST)
		try:
			payment = f.save(commit = False)
			payment.account = account
			payment.user = request.user
			payment.save()
			ItemRecord.objects.get_or_create(payment)
			return HttpResponseRedirect('/admin/billing/receipt/%s/' % (payment.item().receipt.id,))
		except ValueError:
			pass
			
		except DetailAlreadyExists:
			f.errors['chargeAmount'] = (_('Detail Already Exists'),)
	else:
		f = Form()

	context = {
		'account' : account,
		'form' : f,
	}
	t = loader.get_template(template)
	c = RequestContext(request, context)
	return HttpResponse(t.render(c))
