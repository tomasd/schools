from django.conf.urls.defaults import patterns, url
from schools.buildings.models import Building


urlpatterns = patterns('schools.buildings.views',
   url(r'building/create/$', 'building_create', {'model':Building, 'template_name':'buildings/building_create.html'}, name='buildings_building_create'),
   
   url(r'building/(?P<object_id>\d+)/$', 'building_update', name='buildings_building_update'),
   url(r'building/(?P<object_id>\d+)/delete/$', 'building_delete', {'model':Building, 'post_delete_redirect':'buildings_building_list'}, name='buildings_building_delete'),
   
   url(r'building/$', 'building_list', {'queryset':Building.objects.all(), 'search_fields':['name__contains']}, name='buildings_building_list'),
   url(r'classroom/(?P<object_id>\d+)/lessons/$', 'classroom_lessons', name='classroom-lessons',)
)