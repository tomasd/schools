# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from schools.reports.forms import InvoiceForm
from schools.companies.models import Company

def invoice(request):
    if request.GET:
        form = InvoiceForm(request.GET)
        if form.is_valid():
            companies = Company.objects.invoice(companies=form.cleaned_data['companies'],
                                                start=form.cleaned_data['start'],
                                                end=form.cleaned_data['end'])
            total_length = sum([a.invoice_length for a in companies])
            total_price = sum([a.invoice_price for a in companies])
            total_count = sum([a.invoice_count for a in companies])
            context = {'object_list':companies,
                       'total_length':total_length,
                       'total_price':total_price,
                       'total_count':total_count,
                       'show_students':form.cleaned_data['show_students'],
                       }
        else:
            context = { 'nolist':True}
    else:
        context = { 'nolist':True}
        form = InvoiceForm()
    context['form'] = form
    return render_to_response('reports/invoice.html', RequestContext(request, context))
