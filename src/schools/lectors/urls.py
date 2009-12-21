from django.conf.urls.defaults import patterns, url
from django.views.generic.create_update import create_object
from schools.lectors.models import Lector
from schools.search.views import object_list
from generic_views.views.delete import delete_object

urlpatterns = patterns('schools.lectors.views',
    url(r'lector/(?P<lector_id>\d+)/contract/create/$', 'lector_contract_create', name='lectors_contract_create'),
    url(r'lector/(?P<lector_id>\d+)/contract/(?P<object_id>\d+)/$', 'lector_contract_update', name='lectors_contract_update'),
    url(r'lector/(?P<lector_id>\d+)/contract/$', 'lector_contract_list', name='lectors_contract_list'),
    
    url(r'lector/create/$', create_object, {'model':Lector}, name='lectors_lector_create'),
    url(r'lector/(?P<object_id>\d+)/$', 'lector_update', {'model':Lector}, name='lectors_lector_update'),
    url(r'lector/(?P<object_id>\d+)/courses/$', 'lector_courses', name='lectors_lector_courses'),
    url(r'lector/(?P<object_id>\d+)/delete/$', delete_object, {'model':Lector, 'post_delete_redirect':'lectors_lector_list'}, name='lectors_lector_delete'),
    url(r'lector/$', object_list, {'queryset':Lector.objects.all(), 'search_fields':['last_name__contains', 'first_name__contains']}, name='lectors_lector_list'),
    
)