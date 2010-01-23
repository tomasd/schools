# Create your views here.
from django.shortcuts import get_object_or_404
from generic_views.views.create_update import update_object, create_object
from schools.lectors.forms import ContractForm
from schools.lectors.models import Lector, Contract, HourRate
from schools.search.views import object_list
from generic_views.views.delete import delete_object
from schools import permission_required

def lector_contract_list(request, lector_id):
    lector = get_object_or_404(Lector, pk=lector_id)
    return object_list(request, queryset=lector.contract_set.all(), extra_context={'lector':lector})

LECTOR_INLINES = [{'model':HourRate}] 
@permission_required('lectors.add_contract')
def lector_contract_create(request, lector_id):
    lector = get_object_or_404(Lector, pk=lector_id)
    return create_object(request, model=Contract, form_class=ContractForm, initial={'lector':lector.pk}, inlines=LECTOR_INLINES, extra_context={'lector':lector})

@permission_required('lectors.change_contract')
def lector_contract_update(request, lector_id, object_id):
    lector = get_object_or_404(Lector, pk=lector_id)
    return update_object(request, model=Contract, object_id=object_id, form_class=ContractForm, inlines=LECTOR_INLINES, extra_context={'lector':lector})

@permission_required('lectors.delete_contract')
def lector_contract_delete(request, lector_id, object_id):
    get_object_or_404(Lector, pk=lector_id)
    return delete_object(request, model=Contract, object_id=object_id, post_delete_redirect='lectors_contract_list', post_delete_redirect_args=(lector_id,))

@permission_required('lectors.add_lector')
def lector_create(*args, **kwargs):
    return create_object(*args, **kwargs)

@permission_required('lectors.change_lector')
def lector_update(request, *args, **kwargs):
    kwargs['extra_context'] = kwargs.get('extra_context', {})
    kwargs['extra_context']['lector'] = get_object_or_404(Lector, pk=kwargs['object_id'])
    return update_object(request, *args, **kwargs)

@permission_required('lectors.delete_lector')
def lector_delete(*args, **kwargs):
    return delete_object(*args, **kwargs)

@permission_required('lectors.add_lector', 'lectors.change_lector', 'lectors.delete_lector')
def lector_list(*args, **kwargs):
    return object_list(*args, **kwargs)

def lector_courses(request, object_id):
    lector = get_object_or_404(Lector, pk=object_id)
    queryset = lector.course_set.all()
    return object_list(request, ('name__contains', ), queryset=queryset, template_name='lectors/lector_courses.html',
                       extra_context={'lector':lector})