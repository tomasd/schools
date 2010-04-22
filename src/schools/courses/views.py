# Create your views here.
from book_stock.models import BookDelivery
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template.context import RequestContext
from django.utils import simplejson
from django.utils.dateformat import format
from django.utils.translation import ugettext
from django.views.decorators.http import require_POST
from django.views.generic.list_detail import object_list as django_object_list
from fullauthentication.basic_authentication import logged_in_or_basicauth
from generic_views.views.ajax import JSONResponse
from generic_views.views.create_update import update_object, create_object
from generic_views.views.delete import delete_object
from schools import fix_date_boundaries, permission_required
from schools.course_member_references.forms import CourseMemberReferenceForm
from schools.course_member_references.models import CourseMemberReference
from schools.courses.forms import CourseMemberForm, ExpenseGroupForm, \
    LessonPlanForm, LessonRealizedForm, LessonAttendeeForm, CourseMemberCreateForm, \
    ChooseClassroomForm, ReplanLessonForm, LessonSearchForm, LessonRealizedForm1
from schools.courses.models import Course, CourseMember, ExpenseGroup, \
    ExpenseGroupPrice, Lesson, LessonAttendee, lesson_assign_attendees
from schools.genericform.form import PreProcessForm
from schools.search.views import object_list
from schools.students.models import Student
import vobject
from django.contrib.contenttypes.models import ContentType
from book_stock.views import persons_orders

@permission_required('courses.add_course')
def course_create(*args, **kwargs):
    return create_object(*args, **kwargs)

@permission_required('courses.change_course')
def course_update(request, object_id):
    course = get_object_or_404(Course, pk=object_id)
    return update_object(request, model=Course, object_id=object_id, extra_context={'course':course})

@permission_required('courses.delete_course')
def course_delete(*args, **kwargs):
    return delete_object(*args, **kwargs)

@user_passes_test(lambda user:user.has_module_perms('courses'))
def course_list(*args, **kwargs):
    return object_list(*args, **kwargs)

@permission_required('courses.add_coursemember', 'courses.change_coursemember', 'courses.delete_coursemember')
def coursemember_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return object_list(request, queryset=CourseMember.objects.filter(course=course), extra_context={'course':course}, search_fields=['student__first_name__contains', 'student__last_name__contains'])

@permission_required('courses.add_coursemember')
def coursemember_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    form_class = CourseMemberCreateForm#PreProcessForm(CourseMemberCreateForm, lambda form:form.limit_to_course(course))
    return create_object(request, model=CourseMember, form_class=form_class,
                         template_name='courses/coursemember_create.html',
                         extra_context={'course':course}, initial={'course':course.pk},
                         preprocess_form=lambda form:form.limit_to_course(course))

@permission_required('courses.change_coursemember')
def coursemember_update(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    get_object_or_404(course.coursemember_set, pk=object_id)
    inlines = [{'model':CourseMemberReference, 'extra':1, 'form':CourseMemberReferenceForm}]
    return update_object(request, model=CourseMember, form_class=CourseMemberForm, object_id=object_id, extra_context={'course':course}, inlines=inlines)

@permission_required('courses.delete_coursemember')
def coursemember_delete(request, course_id, object_id):
    get_object_or_404(Course, pk=course_id)
    return delete_object(request, model=CourseMember, object_id=object_id, post_delete_redirect='courses_coursemember_list', post_delete_redirect_args=(course_id,))
    
@permission_required('courses.add_expensegroup')
def expensegroup_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return create_object(request, model=ExpenseGroup, form_class=ExpenseGroupForm, template_name='courses/expensegroup_create.html', extra_context={'course':course}, initial={'course':course.pk})

@permission_required('courses.change_expensegroup')
def expensegroup_update(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    inlines = [{'model':ExpenseGroupPrice, 'extra':1}]
    return update_object(request, model=ExpenseGroup, object_id=object_id, extra_context={'course':course, }, inlines=inlines)

@permission_required('courses.add_expensegroup', 'courses.change_expensegroup', 'courses.delete_expensegroup')
def expensegroup_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return object_list(request, queryset=ExpenseGroup.objects.filter(course=course), extra_context={'course':course})

@permission_required('courses.add_lesson')
def lesson_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    LessonFormset = modelformset_factory(Lesson, LessonPlanForm)
    print request
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
        if request.META.get('HTTP_X_REQUESTED_WITH', '') == 'XMLHttpRequest':
            # JSON request, only validate
            formset = LessonFormset(request.GET, queryset=Lesson.objects.none())
            errors = [form.errors for form in formset.forms]
            errors = [dict([(a, b.as_text()) for a, b in error.items()]) for error in errors]
            return HttpResponse(simplejson.dumps(errors,ensure_ascii=False), mimetype='application/json')
        formset = LessonFormset(queryset=Lesson.objects.none(), initial=[{'course':course.pk}])
    context = {'formset': formset, 'course':course, 'choose_classroom_form':ChooseClassroomForm()}
    return render_to_response('courses/lesson_create.html', RequestContext(request, context))
#    course = get_object_or_404(Course, pk=course_id)
#    return create_object(request, model=Lesson, form_class=LessonPlanForm, template_name='courses/lesson_create.html', extra_context={'course':course}, initial={'course':course.pk})
    
@permission_required('courses.change_lesson')
def lesson_update(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    return update_object(request, model=Lesson, form_class=LessonPlanForm, object_id=object_id, extra_context={'course':course, })

@permission_required('courses.change_lesson')
def lesson_attendance(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    lesson = get_object_or_404(course.lesson_set, pk=object_id)
    lesson.fill_attendance()
    lesson_assign_attendees.send(sender=lesson_attendance, lesson=lesson)
    attendee_form_class = PreProcessForm(LessonAttendeeForm, lambda form:form.limit_to_course(course))
    inlines = [{'model':LessonAttendee, 'form':attendee_form_class, 'extra':1}]
    return update_object(request, obj=lesson, form_class=LessonRealizedForm,
                         template_name='courses/lesson_attendance.html',
                         extra_context={'course':course},
                         inlines=inlines, post_save_redirect=lesson.get_attendance_url())

@permission_required('courses.add_lesson', 'courses.change_lesson', 'courses.delete_lesson')
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
    
    return django_object_list(request, queryset=queryset,
                              extra_context={'course':course, 'form':form})

def lesson_attendance_list(request, course_id=None):
    def _remove_course_field(form):
        if course_id is not None: del form.fields['course']
        return form
    if course_id is not None:
        course = get_object_or_404(Course, pk=course_id)
        queryset = course.lesson_set.none()
    else:
        course = None
        queryset = Lesson.objects.none()
        
    if request.GET:
        form = _remove_course_field(LessonSearchForm(request.GET, date_required=True))
        if form.is_valid():
            queryset = Lesson.objects.all() if course is None else course.lesson_set.all() 
            queryset = _search_lessons(queryset, form, date_required=True)
    else:
        form = _remove_course_field(LessonSearchForm(date_required=True))
        
    LessonFormSet = formset_factory(LessonRealizedForm1, extra=0, can_delete=False)
    if request.method == 'POST':
        attendance_formset = LessonFormSet(initial=[{'lesson':lesson.pk} for lesson in queryset.all()], data=request.POST)            
        if attendance_formset.is_valid():
            for form in attendance_formset.forms:
                form.save()
            return redirect(request.get_full_path())
    else:
        attendance_formset = LessonFormSet(initial=[{'lesson':lesson.pk} for lesson in queryset.all()])            
    return render_to_response('courses/lesson_attendance_list.html',
                              {'form':form, 'attendance_formset':attendance_formset, 'course':course},
                              context_instance=RequestContext(request))

@permission_required('courses.change_lesson')
@require_POST
def lesson_replan(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    lesson = get_object_or_404(course.lesson_set, pk=object_id)
    form = ReplanLessonForm(request.POST, instance=lesson)
    if form.is_valid():
        form.save()
        return JSONResponse({'success':True, })
    return  JSONResponse({'success':False, 'errors':form.errors})
        
def _search_lessons(queryset, form, date_required=False):
    if 'course' in form.cleaned_data and form.cleaned_data['course']:
        queryset = queryset.filter(course=form.cleaned_data['course'])
    if form.cleaned_data['start']:
        queryset = queryset.filter(end__gte=form.cleaned_data['start'])
    elif date_required:
        queryset = queryset.none()
    if form.cleaned_data['end']:
        queryset = queryset.filter(start__lt=fix_date_boundaries(form.cleaned_data['end']))
    elif date_required:
        queryset = queryset.none()
    if form.cleaned_data['realized'] is not None:
            queryset = queryset.filter(realized=form.cleaned_data['realized'])
    if form.cleaned_data['building']:
        queryset = queryset.filter(classroom__building=form.cleaned_data['building'])
    if form.cleaned_data['lector']:
        queryset = queryset.filter(course__lector=form.cleaned_data['lector'])
    if form.cleaned_data['classroom']:
        queryset = queryset.filter(classroom=form.cleaned_data['classroom'])
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
                'replan_url':reverse(lesson_replan, kwargs={'course_id':a.course.pk, 'object_id':str(a.pk)}),
                'detail_url':a.get_absolute_url()} 
                for a in lessons]
    text = simplejson.dumps(lessons)
    return HttpResponse(text, mimetype='application/json')

EVENT_ITEMS = (
    ('uid', 'uid'),
    ('dtstart', 'start'),
    ('dtend', 'end'),
    ('summary', 'summary'),
    ('location', 'location'),
    ('last_modified', 'last_modified'),
    ('created', 'created'),
)


@logged_in_or_basicauth('Realm Name')
def lesson_list_ical(request):
    form = LessonSearchForm(request.GET)
    lessons = Lesson.objects.none()
    if form.is_valid():
        lessons = Lesson.objects.all()
        lessons = _search_lessons(lessons, form)
    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this
    for lesson in lessons:
        vevent = cal.add('vevent')
        vevent.add('dtstart').value = lesson.start
        vevent.add('dtend').value = lesson.end
        vevent.add('location').value = unicode(lesson.classroom)
        vevent.add('summary').value = unicode(lesson.course)
        vevent.add('created').value = lesson.created
        vevent.add('last-modified').value = lesson.updated
    icalstream = cal.serialize()
    response = HttpResponse(icalstream, mimetype='text/calendar')
    response['Filename'] = 'lekcie.ics'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=filename.ics'
    return response

def timetable(request):
    form = LessonSearchForm(request.GET)
    return render_to_response('courses/timetable.html', {'form':form}, context_instance=RequestContext(request))

def course_books(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    students = Student.objects.filter(coursemember__course=course)
    student_type = ContentType.objects.get_for_model(Student)
    queryset = BookDelivery.objects.filter(person_id__in=(students), person_type=student_type)
    return object_list(request, queryset=queryset, extra_context={'base':'courses/base.html', 'course':course})

def course_book_orders(request, course_id, template_name='courses/course_book_orders.html', extra_context=None):
    course = get_object_or_404(Course, pk=course_id)
    persons = Student.objects.filter(coursemember__course=course).distinct()
    extra_context = extra_context if extra_context is not None else {}
    extra_context['course'] = course
    return persons_orders(request, persons, template_name=template_name, extra_context=extra_context)