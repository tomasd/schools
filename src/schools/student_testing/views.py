# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template.context import RequestContext
from django.views.generic.list_detail import object_list
from generic_views.views.create_update import update_object
from schools import permission_required
from schools.courses.models import Course
from schools.student_testing.forms import CreateTestResultForm, \
    CreateTestingTermForm, TestResultForm, EditTestResultForm, TestingTermForm
from schools.student_testing.models import TestingTerm, TestResult
import operator
from django.views.generic.create_update import delete_object
from django.core.urlresolvers import reverse

@permission_required('student_testing.add_testingterm')
def create_test_result(request, object_id):
    def _create_forms(course, data=None):
        for course_member in course.coursemember_set.all():
                if request.user.has_perm('student_testing.add_testresult'):
                    yield course_member, CreateTestResultForm(data=data, prefix=str(course_member.pk), initial={'course_member':course_member.pk})
    def acl(form):
        if not request.user.has_perm('student_testing.add_studenttest'):
            del form.fields['name']
            del form.fields['description']
            del form.fields['max_score']
        return form
    course = get_object_or_404(Course, pk=object_id)
    
    if request.method =='POST':
        form = acl(CreateTestingTermForm(request.POST, prefix="testing"))
        forms = list(_create_forms(course, data=request.POST))
        if form.is_valid() and (reduce(operator.__and__, [a.is_valid() for k, a in forms]) if forms else True): #@UnusedVariable
            test = form.save()
            results = [a.save(False) for x, a in forms] #@UnusedVariable
            for result in results:
                result.testing_term = test
                result.save()
            return redirect(test)
    else:
        form = acl(CreateTestingTermForm(prefix="testing", initial={'course':course.pk}))
        forms = list(_create_forms(course))
    return render_to_response('student_testing/create_testing_term.html', 
                              {'form':form, 'form_results':forms,'course':course}, 
                              context_instance=RequestContext(request))

@permission_required('student_testing.change_testingterm')
def update_test_result(request, course_id, object_id):
    def acl(formset):
        for f in formset.forms:
            f.limit_to_course(course) 
    test = get_object_or_404(TestingTerm, pk=object_id)
    course = get_object_or_404(Course, pk=course_id)
    inlines = [{'model':TestResult, 'extra':1, 'form':EditTestResultForm}]
    return update_object(request, obj=test, model=TestingTerm,form_class=TestingTermForm,
                         template_name='student_testing/update_testing_term.html', 
                         extra_context={'course':course,}, 
                         inlines=inlines, preprocess_formset=acl)
    
def list_test_result(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return object_list(request, queryset=course.testingterm_set.all(), template_name='student_testing/testing_term_list.html', extra_context={'course':course})

@permission_required('student_testing.delete_testingterm')
def delete_testing_term(request, *args, **kwargs):
    term = get_object_or_404(TestingTerm, pk=kwargs['object_id'])
    redirect = term.course.get_testing_url()
    return delete_object(request, post_delete_redirect=redirect, *args, **kwargs)