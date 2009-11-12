# Create your views here.
from generic_views.views.create_update import update_object
from django.shortcuts import get_object_or_404
from schools.companies.models import Company
def company_update(request, *args, **kwargs):
    kwargs['extra_context'] = kwargs.get('extra_context', {})
    kwargs['extra_context']['company'] = get_object_or_404(Company, pk=kwargs['object_id'])
    return update_object(request, *args, **kwargs)