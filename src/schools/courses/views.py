# Create your views here.
from django.shortcuts import get_object_or_404
from generic_views.views.create_update import update_object, create_object
from schools.courses.forms import CourseMemberForm, ExpenseGroupForm, \
    LessonPlanForm, LessonRealizedForm, LessonAttendeeForm,\
    CourseMemberCreateForm
from schools.courses.models import Course, CourseMember, ExpenseGroup, \
    ExpenseGroupPrice, Lesson, LessonAttendee, lesson_assign_attendees
from schools.genericform.form import PreProcessForm
from schools.search.views import object_list

def course_update(request, object_id):
    course = get_object_or_404(Course, pk=object_id)
    return update_object(request, model=Course, object_id=object_id, extra_context={'course':course})

def coursemember_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return object_list(request, queryset=CourseMember.objects.filter(course=course), extra_context={'course':course}, search_fields=['student__first_name__contains', 'student__last_name__contains'])

def coursemember_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    form_class = PreProcessForm(CourseMemberCreateForm, lambda form:form.limit_to_course(course))
    return create_object(request, model=CourseMember, form_class=form_class, template_name='courses/coursemember_create.html', extra_context={'course':course}, initial={'course':course.pk})

def coursemember_update(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    get_object_or_404(course.coursemember_set, pk=object_id)
    return update_object(request, model=CourseMember, form_class=CourseMemberForm, object_id=object_id, extra_context={'course':course})

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
    lesson = get_object_or_404(course.lesson_set, pk=object_id)
    lesson_assign_attendees.send(sender=lesson_attendance, lesson=lesson)
    attendee_form_class = PreProcessForm(LessonAttendeeForm, lambda form:form.limit_to_course(course))
    inlines = [{'model':LessonAttendee, 'form':attendee_form_class, 'extra':1}]
    return update_object(request, model=Lesson, form_class=LessonRealizedForm, 
                         template_name='courses/lesson_attendance.html', 
                         object_id=object_id, extra_context={'course':course,}, 
                         inlines=inlines,post_save_redirect=lesson.get_attendance_url())

def lesson_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)    
    return object_list(request, queryset=Lesson.objects.filter(course=course), extra_context={'course':course,})