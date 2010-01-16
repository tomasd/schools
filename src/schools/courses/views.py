# Create your views here.
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template.context import RequestContext
from django.utils import simplejson
from django.utils.dateformat import format
from django.utils.translation import ugettext
from django.views.decorators.http import require_POST
from django.views.generic.list_detail import object_list as django_object_list
from generic_views.views.ajax import JSONResponse
from generic_views.views.create_update import update_object, create_object
from generic_views.views.delete import delete_object
from schools import fix_date_boundaries
from schools.course_member_references.models import CourseMemberReference
from schools.courses.forms import CourseMemberForm, ExpenseGroupForm, \
    LessonPlanForm, LessonRealizedForm, LessonAttendeeForm, CourseMemberCreateForm, \
    ChooseClassroomForm, ReplanLessonForm, LessonSearchForm
from schools.courses.models import Course, CourseMember, ExpenseGroup, \
    ExpenseGroupPrice, Lesson, LessonAttendee, lesson_assign_attendees
from schools.genericform.form import PreProcessForm
from schools.search.views import object_list
from schools.course_member_references.forms import CourseMemberReferenceForm

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
    inlines = [{'model':CourseMemberReference, 'extra':1, 'form':CourseMemberReferenceForm}]
    return update_object(request, model=CourseMember, form_class=CourseMemberForm, object_id=object_id, extra_context={'course':course}, inlines=inlines)

def coursemember_delete(request, course_id, object_id):
    return delete_object(request, model=CourseMember, object_id=object_id, post_delete_redirect='courses_coursemember_list', post_delete_redirect_args=(course_id,))
    
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
    LessonFormset = modelformset_factory(Lesson, LessonPlanForm)
    if request.method == 'POST':
        formset = LessonFormset(request.POST, queryset=Lesson.objects.none())
        if formset.is_valid():
            lessons = formset.save()
            if request.user.is_authenticated():
                for lesson in lessons:
                    request.user.message_set.create(message=ugettext("The %(verbose_name)s was created successfully.") % {"verbose_name": lesson._meta.verbose_name})
            if len(lessons) == 1: 
                return redirect(lessons[0])
            else:
                return redirect(reverse(lesson_list, kwargs={'course_id':course_id}))
    else:
        formset = LessonFormset(queryset=Lesson.objects.none(), initial=[{'course':course.pk}])
    context = {'formset': formset, 'course':course, 'choose_classroom_form':ChooseClassroomForm()}
    return render_to_response('courses/lesson_create.html', RequestContext(request,context))
#    course = get_object_or_404(Course, pk=course_id)
#    return create_object(request, model=Lesson, form_class=LessonPlanForm, template_name='courses/lesson_create.html', extra_context={'course':course}, initial={'course':course.pk})
    
def lesson_update(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    return update_object(request, model=Lesson, form_class=LessonPlanForm, object_id=object_id, extra_context={'course':course,})

def lesson_attendance(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    lesson = get_object_or_404(course.lesson_set, pk=object_id)
    lesson.fill_attendance()
    lesson_assign_attendees.send(sender=lesson_attendance, lesson=lesson)
    attendee_form_class = PreProcessForm(LessonAttendeeForm, lambda form:form.limit_to_course(course))
    inlines = [{'model':LessonAttendee, 'form':attendee_form_class, 'extra':1}]
    return update_object(request, obj=lesson, form_class=LessonRealizedForm, 
                         template_name='courses/lesson_attendance.html', 
                         extra_context={'course':course,}, 
                         inlines=inlines,post_save_redirect=lesson.get_attendance_url())

def lesson_list(request, course_id):
    def _remove_course_field(form):
        del form.fields['course']
        return form
    course = get_object_or_404(Course, pk=course_id)
    queryset = course.lesson_set.all()
    if request.GET:
        form = _remove_course_field(LessonSearchForm(request.GET))
        if form.is_valid():
            queryset = _search_lessons(queryset, form)
    else:
        form = _remove_course_field(LessonSearchForm())
    return django_object_list(request, queryset=queryset, extra_context={'course':course, 'form':form})


@require_POST
def lesson_replan(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    lesson = get_object_or_404(course.lesson_set, pk=object_id)
    form = ReplanLessonForm(request.POST, instance=lesson)
    if form.is_valid():
        form.save()
        return JSONResponse({'success':True, })
    return  JSONResponse({'success':False, 'errors':form.errors})
        
def _search_lessons(queryset, form):
    if form.cleaned_data['course']:
        queryset = queryset.filter(course=form.cleaned_data['course'])
    if form.cleaned_data['start']:
        queryset = queryset.filter(end__gte=form.cleaned_data['start'])
    if form.cleaned_data['end']:
        queryset = queryset.filter(start__lt=fix_date_boundaries(form.cleaned_data['end']))
    if form.cleaned_data['realized'] is not None:
            queryset = queryset.filter(realized=form.cleaned_data['realized'])
    if form.cleaned_data['building']:
        queryset = queryset.filter(classroom__building=form.cleaned_data['building'])
    if form.cleaned_data['lector']:
        queryset = queryset.filter(course__lector=form.cleaned_data['lector'])
    return queryset

def courses_lessons(request):
    queryset = Lesson.objects.none()
    
    if request.GET:
        queryset = Lesson.objects.all()
        form = LessonSearchForm(request.GET)
        if form.is_valid():
            queryset = _search_lessons(queryset, form)
    else:
        form = LessonSearchForm()
    
    return django_object_list(request, queryset=queryset, template_name='courses/lesson_list.html', extra_context={'form':form})

def lesson_list_json(request):
#    course = get_object_or_404(Course, pk=course_id)
    form = LessonSearchForm(request.GET)
    lessons = Lesson.objects.none()
    if form.is_valid():
        lessons = Lesson.objects.all()
        lessons = _search_lessons(lessons, form)
    lessons = [{'id':a.pk,
                'start':format(a.start, 'Y-m-d\TH:i:s.000O'), 
                'end':format(a.end, 'Y-m-d\TH:i:s.000O'),
                'title':u'%s - %s' % (a.classroom, a.course),
                'replan_url':reverse(lesson_replan, kwargs={'course_id':a.course.pk, 'object_id':str(a.pk)})} 
                for a in lessons]
    text = simplejson.dumps(lessons)
    return HttpResponse(text, mimetype='application/json')