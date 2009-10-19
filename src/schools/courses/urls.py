from django.conf.urls.defaults import patterns, url
from django.views.generic.create_update import create_object
from schools.courses.models import Course
from schools.search.views import object_list

urlpatterns = patterns('schools.courses.views',
    url(r'course/(?P<course_id>\d+)/member/create/$', 'coursemember_create', name='courses_coursemember_create'),
    url(r'course/(?P<course_id>\d+)/member/(?P<object_id>\d+)/$', 'coursemember_update', name='courses_coursemember_update'),
    url(r'course/(?P<course_id>\d+)/member/$', 'coursemember_list', name='courses_coursemember_list'),
    
    url(r'course/(?P<course_id>\d+)/expense/create/$', 'expensegroup_create', name='courses_expensegroup_create'),
    url(r'course/(?P<course_id>\d+)/expense/(?P<object_id>\d+)/$', 'expensegroup_update', name='courses_expensegroup_update'),
    url(r'course/(?P<course_id>\d+)/expense/$', 'expensegroup_list', name='courses_expensegroup_list'),
    
    url(r'course/(?P<course_id>\d+)/lesson/create/$', 'lesson_create', name='courses_lesson_create'),
    url(r'course/(?P<course_id>\d+)/lesson/(?P<object_id>\d+)/attendance/$', 'lesson_attendance', name='courses_lesson_attendance'),
    url(r'course/(?P<course_id>\d+)/lesson/(?P<object_id>\d+)/$', 'lesson_update', name='courses_lesson_update'),
    url(r'course/(?P<course_id>\d+)/lesson/$', 'lesson_list', name='courses_lesson_list'),
    
    
    url(r'course/create/$', create_object, {'model':Course, 'template_name':'courses/course_create.html'}, name='courses_course_create'),
    url(r'course/(?P<object_id>\d+)/$', 'course_update', name='courses_course_update'),
    url(r'course/$', object_list, {'queryset':Course.objects.all(), 'search_fields':['name__contains']}, name='courses_course_list'),
    
)