# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
from django.views.generic.create_update import update_object, create_object
from django.views.generic.list_detail import object_list
from schools.courses.forms import CourseForm, CourseMemberForm, ExpenseGroupForm
from schools.courses.models import Course, CourseMember, ExpenseGroup,\
    ExpenseGroupPrice
from django.forms.models import inlineformset_factory

def course_update(request, object_id):
    course = get_object_or_404(Course, pk=object_id)
    return update_object(request, model=Course, object_id=object_id, extra_context={'course':course})

def coursemember_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return object_list(request, queryset=CourseMember.objects.filter(course=course), extra_context={'course':course})

def coursemember_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = CourseMemberForm(data=request.POST)
        if form.is_valid():
            return redirect(form.save())
    else:
        form = CourseMemberForm(initial={'course':course.pk})
            
    context = {'form':form,
               'course':course}
    return render_to_response('courses/coursemember_create.html', RequestContext(request, context))

def coursemember_update(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    get_object_or_404(course.coursemember_set, pk=object_id)
    return update_object(request, model=CourseMember, object_id=object_id, extra_context={'course':course})

def expensegroup_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    if request.method == 'POST':
        form = ExpenseGroupForm(data=request.POST)
        if form.is_valid():
            return redirect(form.save())
    else:
        form= ExpenseGroupForm(initial={'course':course.pk})
    
    context = {'form':form,
               'course':course}
    return render_to_response('courses/expensegroup_create.html', RequestContext(request, context))

def expensegroup_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return object_list(request, queryset=ExpenseGroup.objects.filter(course=course), extra_context={'course':course})

def expensegroup_update(request, course_id, object_id):
    course = get_object_or_404(Course, pk=course_id)
    expense_group = get_object_or_404(course.expensegroup_set, pk=object_id)
    ExpenseGroupPriceFormset = inlineformset_factory(ExpenseGroup, ExpenseGroupPrice, extra=1)
    
    if request.method == 'POST':
        form = ExpenseGroupForm(data=request.POST, instance=expense_group)
        expensegroupprice_formset = ExpenseGroupPriceFormset(data=request.POST, prefix='price', instance=expense_group)
        if form.is_valid() and expensegroupprice_formset.is_valid():
            expensegroupprice_formset.save()
            return redirect(form.save())
    else:
        form = ExpenseGroupForm(initial={'course':course.pk}, instance=expense_group)
        expensegroupprice_formset = ExpenseGroupPriceFormset(prefix='price', instance=expense_group)
    context = {'expensegroup_form':form,
               'course':course,
               'expensegroupprice_formset':expensegroupprice_formset}
    return render_to_response('courses/expensegroup_form.html', RequestContext(request, context))