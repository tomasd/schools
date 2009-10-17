from django.conf.urls.defaults import patterns, url
from django.views.generic.create_update import create_object, update_object
from django.views.generic.list_detail import object_list
from schools.students.models import Student

urlpatterns = patterns('',
    url(r'student/create/$', create_object, {'model':Student}, name='students_student_create'),
    url(r'student/(?P<object_id>\d+)/$', update_object, {'model':Student}, name='students_student_update'),
    url(r'student/$', object_list, {'queryset':Student.objects.all()}, name='students_student_list'),
    
)