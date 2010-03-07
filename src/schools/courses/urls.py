from django.conf.urls.defaults import patterns, url
from schools.courses.models import Course
from schools.student_testing.views import create_test_result, update_test_result, \
    list_test_result

urlpatterns = patterns('schools.courses.views',
    url(r'course/(?P<course_id>\d+)/member/create/$', 'coursemember_create', name='courses_coursemember_create'),
    url(r'course/(?P<course_id>\d+)/member/(?P<object_id>\d+)/$', 'coursemember_update', name='courses_coursemember_update'),
    url(r'course/(?P<course_id>\d+)/member/(?P<object_id>\d+)/delete/$', 'coursemember_delete', name='courses_coursemember_delete'),
    url(r'course/(?P<course_id>\d+)/member/$', 'coursemember_list', name='courses_coursemember_list'),
    
    url(r'course/(?P<course_id>\d+)/expense/create/$', 'expensegroup_create', name='courses_expensegroup_create'),
    url(r'course/(?P<course_id>\d+)/expense/(?P<object_id>\d+)/$', 'expensegroup_update', name='courses_expensegroup_update'),
    url(r'course/(?P<course_id>\d+)/expense/$', 'expensegroup_list', name='courses_expensegroup_list'),
    
    url(r'course/(?P<course_id>\d+)/lesson/create/$', 'lesson_create', name='courses_lesson_create'),
    url(r'course/(?P<course_id>\d+)/lesson/(?P<object_id>\d+)/attendance/$', 'lesson_attendance', name='courses_lesson_attendance'),
    url(r'course/(?P<course_id>\d+)/lesson/(?P<object_id>\d+)/$', 'lesson_update', name='courses_lesson_update'),
    url(r'course/(?P<course_id>\d+)/lesson/(?P<object_id>\d+)/replan/$', 'lesson_replan', name='courses_lesson_replan'),
    url(r'course/(?P<course_id>\d+)/lesson/$', 'lesson_list', name='courses_lesson_list'),
    url(r'course/(?P<course_id>\d+)/lesson/attendance/$', 'lesson_attendance_list', name='courses_course_lesson_attendance_list'),
    
    url(r'course/lessons/json/$', 'lesson_list_json', name='courses_lesson_list_json'),
    url(r'course/lessons/$', 'courses_lessons', name='courses_lessons'),
    url(r'course/lessons/attendance/$', 'lesson_attendance_list', name='courses_lesson_attendance_list'),
    
    url(r'course/(?P<object_id>\d+)/testing/create/$', create_test_result, name='courses_course_test_result_create'),
    url(r'course/(?P<course_id>\d+)/testing/(?P<object_id>\d+)/$', update_test_result, name='courses_course_test_result_update'),
    url(r'course/(?P<course_id>\d+)/testing/$', list_test_result, name='courses_course_test_result_list'),
    
    url(r'course/create/$', 'course_create', {'model':Course, 'template_name':'courses/course_create.html'}, name='courses_course_create'),
    url(r'course/(?P<object_id>\d+)/$', 'course_update', name='courses_course_update'),
    url(r'course/(?P<object_id>\d+)/delete/$', 'course_delete', {'model':Course, 'post_delete_redirect':'courses_course_list'}, name='courses_course_delete'),
    url(r'course/$', 'course_list', {'queryset':Course.objects.all(), 'search_fields':['name__contains']}, name='courses_course_list'),
    
    url(r'time-table/$', 'timetable', name='courses_time-table'),
    
)
