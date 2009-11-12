# Create your views here.
from django.shortcuts import get_object_or_404
from generic_views.views.create_update import update_object, create_object
from schools.lectors.forms import ContractForm
from schools.lectors.models import Lector, Contract, HourRate
from schools.search.views import object_list

def lector_contract_list(request, lector_id):
    lector = get_object_or_404(Lector, pk=lector_id)
    return object_list(request, queryset=lector.contract_set.all(), extra_context={'lector':lector})

LECTOR_INLINES = [{'model':HourRate}] 
def lector_contract_create(request, lector_id):
    lector = get_object_or_404(Lector, pk=lector_id)
    return create_object(request, model=Contract, form_class=ContractForm, initial={'lector':lector.pk}, inlines=LECTOR_INLINES, extra_context={'lector':lector})

def lector_contract_update(request, lector_id, object_id):
    lector = get_object_or_404(Lector, pk=lector_id)
    return update_object(request, model=Contract, object_id=object_id, form_class=ContractForm, inlines=LECTOR_INLINES, extra_context={'lector':lector})

def lector_update(request, *args, **kwargs):
    kwargs['extra_context'] = kwargs.get('extra_context', {})
    kwargs['extra_context']['lector'] = get_object_or_404(Lector, pk=kwargs['object_id'])
    return update_object(request, *args, **kwargs)
