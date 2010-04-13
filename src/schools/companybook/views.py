# Create your views here.
from django.http import Http404
from django.shortcuts import get_list_or_404
from schools.companies.models import Company
from schools.reports.views import invoice, book_invoice_dict
from schools.search.views import object_list

def companybook(request):
    companies = Company.objects.filter(users=request.user)
    if not companies:
        raise Http404()
    book_context = book_invoice_dict(request, companies, companies)
    book_context = dict([('book_%s' % key, value) for key, value in book_context.items()])
    extra_context = {'companies':companies}
    extra_context.update(book_context)
    return invoice(request, 
                   companies=companies, 
                   template='companybook/companybook.html', 
                   extra_context=extra_context)
    
def company_students(request):
    from schools.students.models import Student
    companies = Company.objects.filter(users=request.user)
    return object_list(request, search_fields=('first_name__contains', 'last_name__contains','company__name__contains'),
                       queryset=Student.objects.filter(company__in=companies),
                       template_name='companybook/company_students.html' )