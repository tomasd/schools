# Create your views here.
from django.shortcuts import get_list_or_404
from schools.companies.models import Company
from schools.reports.views import invoice
from django.http import Http404

def companybook(request):
    companies = Company.objects.filter(users=request.user)
    if not companies:
        raise Http404()
    return invoice(request, companies=companies, template='companybook/companybook.html', extra_context={'companies':companies})