# Create your views here.
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template.context import RequestContext
from generic_views.views.create_update import update_object, create_object
from generic_views.views.delete import delete_object
from schools import permission_required
from schools.companies.forms import CompanyUserForm, CompanyUserCreationForm
from schools.companies.models import Company
from schools.search.views import object_list

@permission_required('companies.add_company')
def company_create(*args, **kwargs):
    return create_object(*args, **kwargs)

@permission_required('companies.change_company')
def company_update(request, *args, **kwargs):
    kwargs['extra_context'] = kwargs.get('extra_context', {})
    kwargs['extra_context']['company'] = get_object_or_404(Company, pk=kwargs['object_id'])
    return update_object(request, *args, **kwargs)

@permission_required('companies.delete_company')
def company_delete(*args, **kwargs):
    return delete_object(*args, **kwargs)

@permission_required('companies.add_company', 'companies.change_company', 'companies.delete_company')
def company_list(*args, **kwargs):
    return object_list(*args, **kwargs)

def company_students(request, object_id):
    company = get_object_or_404(Company, pk=object_id)
    queryset = company.student_set.all()
    return object_list(request, ('last_name__contains', 'first_name__contains'), queryset=queryset, template_name='companies/company_students.html',
                       extra_context={'company':company})
    
def company_users(request, object_id):
    company = get_object_or_404(Company, pk=object_id)
    queryset = company.users.all()
    return object_list(request, ('login__contains', 'last_name__contains', 'first_name__contains'), queryset=queryset, template_name='companies/company_users.html' ,
                       extra_context={'company':company})
    
def company_user_update(request, company_id, object_id):
    return update_object(request, object_id = object_id, form_class = CompanyUserForm, model = User, extra_context = {'company':get_object_or_404(Company, pk=company_id)}, template_name = 'companies/company_user_form.html',
                         post_save_redirect = reverse('companies_company_user_update', args=(company_id, object_id,)))

def company_user_create(request, object_id):
    company = get_object_or_404(Company, pk=object_id)
    if request.method == 'POST':
        form = CompanyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            company.users.add(user)
            return redirect(reverse('companies_company_user_update', args=(str(company.pk), str(user.pk),)))
    else:
        form = CompanyUserCreationForm()
    return render_to_response('companies/company_user_form.html', {'form':form, 'company':company}, 
                              context_instance=RequestContext(request))