# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from schools.students.models import Student
from schools.reports.forms import InvoiceForm

def invoice(request):
    if request.GET:
        form = InvoiceForm(request.GET)
        if form.is_valid():
            students = Student.objects.invoice(**form.cleaned_data)
            total_length = sum([a.invoice_length for a in students])
            total_price = sum([a.invoice_price for a in students])
            total_count = sum([a.invoice_count for a in students])
            context = {'object_list':students,
                       'total_length':total_length,
                       'total_price':total_price,
                       'total_count':total_count,
                       }
        else:
            context = { 'nolist':True}
    else:
        context = { 'nolist':True}
        form = InvoiceForm()
    context['form'] = form
    return render_to_response('reports/invoice.html', RequestContext(request, context))
