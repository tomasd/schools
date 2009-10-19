# Create your views here.
from django.db.models.query_utils import Q
from django.views.generic.list_detail import object_list as generic_object_list
from schools.search.forms import SearchForm
import operator

def object_list(request, search_fields=[], *args, **kwargs):
    queryset = kwargs['queryset']
    
    if request.GET and search_fields:
        form = SearchForm(request.GET)
        if form.is_valid():
            q = form.cleaned_data['q']
            queryset = queryset.filter(reduce(operator.or_, [Q(**{field:term}) for term in q.split() for field in search_fields] ))
    else:
        form = SearchForm()
    kwargs['extra_context'] = kwargs.get('extra_context', {})
    kwargs['extra_context']['form'] = form
    kwargs['queryset'] = queryset
    return generic_object_list(request, *args, **kwargs)
