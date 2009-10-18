# Create your views here.
from django.shortcuts import get_object_or_404
from generic_views.views.create_update import update_object
from schools.lectors.models import Lector

def lector_update(request, *args, **kwargs):
    kwargs['extra_context'] = kwargs.get('extra_context', {})
    kwargs['extra_context']['lector'] = get_object_or_404(Lector, pk=kwargs['object_id'])
    return update_object(request, *args, **kwargs)