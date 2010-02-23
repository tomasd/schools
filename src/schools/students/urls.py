from django.conf.urls.defaults import patterns, url
from schools.students.models import Student
from schools.students.forms import CreateStudentForm

urlpatterns = patterns('schools.students.views',
    url(r'student/create/$', 'student_create', {'model':Student, 'form_class':CreateStudentForm}, name='students_student_create'),
    url(r'student/(?P<object_id>\d+)/$', 'student_update', name='students_student_update'),
    url(r'student/(?P<object_id>\d+)/courses/$', 'student_courses', name='students_student_courses'),
    url(r'student/(?P<object_id>\d+)/delete/$', 'student_delete', {'model':Student, 'post_delete_redirect':'students_student_list'}, name='students_student_delete'),
    url(r'student/(?P<object_id>\d+)/set-password/$', 'student_user_set_password', name='students_student_set_password'),
    url(r'student/$', 'student_list', {'queryset':Student.objects.all(), 'search_fields':['last_name__contains', 'first_name__contains']}, name='students_student_list'),
    
)