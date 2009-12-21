# Create your views here.
from generic_views.views.create_update import update_object
from django.shortcuts import get_object_or_404
from schools.companies.models import Company
from schools.search.views import object_list
def company_update(request, *args, **kwargs):
    kwargs['extra_context'] = kwargs.get('extra_context', {})
    kwargs['extra_context']['company'] = get_object_or_404(Company, pk=kwargs['object_id'])
    return update_object(request, *args, **kwargs)

def company_students(request, object_id):
    company = get_object_or_404(Company, pk=object_id)
    queryset = company.student_set.all()
    return object_list(request, ('last_name__contains', 'first_name__contains'), queryset=queryset, template_name='companies/company_students.html',
                       extra_context={'company':company})