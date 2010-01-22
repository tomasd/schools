# Create your views here.
from generic_views.views.create_update import update_object, create_object
from django.shortcuts import get_object_or_404
from schools.companies.models import Company
from schools.search.views import object_list
from schools import permission_required
from generic_views.views.delete import delete_object

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