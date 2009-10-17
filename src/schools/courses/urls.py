from django.conf.urls.defaults import patterns, url
from django.views.generic.create_update import create_object, update_object
from django.views.generic.list_detail import object_list
from schools.courses.models import Course

urlpatterns = patterns('',
    url(r'course/create/$', create_object, {'model':Course}, name='courses_course_create'),
    url(r'course/(?P<object_id>\d+)/$', update_object, {'model':Course}, name='courses_course_update'),
    url(r'course/$', object_list, {'queryset':Course.objects.all()}, name='courses_course_list'),
)