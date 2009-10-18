from django.conf.urls.defaults import patterns, url
from django.views.generic.create_update import create_object, update_object
from django.views.generic.list_detail import object_list
from schools.lectors.models import Lector

urlpatterns = patterns('schools.lectors.views',
    url(r'lector/create/$', create_object, {'model':Lector}, name='lectors_lector_create'),
    url(r'lector/(?P<object_id>\d+)/$', 'lector_update', {'model':Lector}, name='lectors_lector_update'),
    url(r'lector/$', object_list, {'queryset':Lector.objects.all()}, name='lectors_lector_list'),
    
)