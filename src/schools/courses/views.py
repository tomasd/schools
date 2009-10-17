# Create your views here.
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from generic_views.views.create_update import update_object, create_object
from schools.courses.forms import CourseMemberForm, ExpenseGroupForm, \
     LessonPlanForm, LessonRealizedForm
from schools.courses.models import Course, CourseMember, ExpenseGroup, \
    ExpenseGroupPrice, Lesson, LessonAttendee

def course_update(request, object_id):
    course = get_object_or_404(Course, pk=object_id)
    return update_object(request, model=Course, object_id=object_id, extra_context={'course':course})

def coursemember_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return object_list(request, queryset=CourseMember.objects.filter(course=course), extra_context={'course':course})

def coursemember_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return create_object(request, model=CourseMember, form_class=CourseMemberForm, template_name='courses/coursemember_create.html', extra_context={'course':course}, initial={'course':course.pk})

def coursemember_update(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    get_object_or_404(course.coursemember_set, pk=object_id)
    return update_object(request, model=CourseMember, object_id=object_id, extra_context={'course':course})

def expensegroup_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return create_object(request, model=ExpenseGroup, form_class=ExpenseGroupForm, template_name='courses/expensegroup_create.html', extra_context={'course':course}, initial={'course':course.pk})

def expensegroup_update(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    inlines = [{'model':ExpenseGroupPrice, 'extra':1}]
    return update_object(request, model=ExpenseGroup, object_id=object_id, extra_context={'course':course,}, inlines=inlines)

def expensegroup_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return object_list(request, queryset=ExpenseGroup.objects.filter(course=course), extra_context={'course':course})


def lesson_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return create_object(request, model=Lesson, form_class=LessonPlanForm, template_name='courses/lesson_create.html', extra_context={'course':course}, initial={'course':course.pk})
    
def lesson_update(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    return update_object(request, model=Lesson, form_class=LessonPlanForm, object_id=object_id, extra_context={'course':course,})

def lesson_attendance(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    inlines = [{'model':LessonAttendee, 'extra':1}]
    return update_object(request, model=Lesson, form_class=LessonRealizedForm, template_name='courses/lesson_attendance.html', object_id=object_id, extra_context={'course':course,}, inlines=inlines)

def lesson_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)    
    return object_list(request, queryset=Lesson.objects.filter(course=course), extra_context={'course':course,})