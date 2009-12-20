from django.conf.urls.defaults import patterns, url
from django.views.generic.create_update import create_object
from generic_views.views.delete import delete_object
from schools.buildings.models import Building
from schools.search.views import object_list


urlpatterns = patterns('schools.buildings.views',
   url(r'building/create/$', create_object, {'model':Building, 'template_name':'buildings/building_create.html'}, name='buildings_building_create'),
   
   url(r'building/(?P<object_id>\d+)/$', 'building_update', name='buildings_building_update'),
   url(r'building/(?P<object_id>\d+)/delete/$', delete_object, {'model':Building, 'post_delete_redirect':'buildings_building_list'}, name='buildings_building_delete'),
   
   url(r'building/$', object_list, {'queryset':Building.objects.all(), 'search_fields':['name__contains']}, name='buildings_building_list'),
   url(r'classroom/(?P<object_id>\d+)/lessons/$', 'classroom_lessons', name='classroom-lessons',)
)