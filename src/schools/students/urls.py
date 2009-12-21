from django.conf.urls.defaults import patterns, url
from generic_views.views.create_update import create_object
from generic_views.views.delete import delete_object
from schools.search.views import object_list
from schools.students.models import Student

urlpatterns = patterns('schools.students.views',
    url(r'student/create/$', create_object, {'model':Student}, name='students_student_create'),
    url(r'student/(?P<object_id>\d+)/$', 'update_student', name='students_student_update'),
    url(r'student/(?P<object_id>\d+)/courses/$', 'student_courses', name='students_student_courses'),
    url(r'student/(?P<object_id>\d+)/delete/$', delete_object, {'model':Student, 'post_delete_redirect':'students_student_list'}, name='students_student_delete'),
    url(r'student/$', object_list, {'queryset':Student.objects.all(), 'search_fields':['last_name__contains', 'first_name__contains']}, name='students_student_list'),
    
)