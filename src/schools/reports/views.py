# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from schools.companies.models import Company
from schools.courses.models import Course
from schools.lectors.models import Lector
from schools.reports.forms import InvoiceForm, LessonAnalysisForm, \
    LessonPlanForm, CompanyAddedValueForm

def invoice(request):
    if request.GET:
        form = InvoiceForm(request.GET)
        if form.is_valid():
            companies = Company.objects.invoice(companies=form.cleaned_data['companies'],
                                                start=form.cleaned_data['start'],
                                                end=form.cleaned_data['end'])
            total_length = sum([a.invoice_length for a in companies])
            total_price = sum([a.invoice_price for a in companies])
            total_count = sum([a.invoice_count for a in companies])
            context = {'object_list':companies,
                       'total_length':total_length,
                       'total_price':total_price,
                       'total_count':total_count,
                       'show_students':form.cleaned_data['show_students'],
                       }
        else:
            context = { 'nolist':True}
    else:
        context = { 'nolist':True}
        form = InvoiceForm()
    context['form'] = form
    return render_to_response('reports/invoice.html', RequestContext(request, context))

def lesson_analysis(request):
    lectors = Lector.objects.none()
    show_courses = True
    if request.GET:
        form = LessonAnalysisForm(request.GET)
        if form.is_valid():
            lectors = Lector.objects.lesson_analysis(form.cleaned_data['start'], form.cleaned_data['end'])
            show_courses = form.cleaned_data['show_courses']
    else:
        form = LessonAnalysisForm()
    
    total_length = sum([a.analysis_length for a in lectors])
    total_price = sum([a.analysis_price for a in lectors])
    context = {'object_list':lectors,
               'total_length':total_length,
               'total_price':total_price,
               'form':form,
               'show_courses':show_courses,
               }
    return render_to_response('reports/lesson_analysis.html', RequestContext(request, context))

def course_plan(request):
    courses = Course.objects.none()
    if request.GET:
        form = LessonPlanForm(request.GET)
        if form.is_valid():
            courses = Course.objects.course_plan(form.cleaned_data['start'], form.cleaned_data['end'])
    else:
        form = LessonPlanForm()
    
    total_lesson_hours = sum([a.course_plan.lesson_hours for a in courses])
    total_price = sum([a.course_plan.price for a in courses])
    context = {'object_list':courses,
               'total_lesson_hours':total_lesson_hours,
               'total_price':total_price,
               'form':form,
#               'show_courses':show_courses,
               }
    return render_to_response('reports/course_plan.html', RequestContext(request, context))

def company_added_value(request):
    companies = Company.objects.none()
    if request.GET:
        form = CompanyAddedValueForm(request.GET)
        if form.is_valid():
            companies = Company.objects.added_value(companies=form.cleaned_data['companies'],
                                                start=form.cleaned_data['start'],
                                                end=form.cleaned_data['end'])
    else:
        form = InvoiceForm()
    total_length = sum([a.invoice_length for a in companies])
    total_price = sum([a.invoice_price for a in companies])
    total_count = sum([a.invoice_count for a in companies])
    total_building_price = sum([a.invoice_building_price for a in companies])
    total_lector_price = sum([a.invoice_lector_price for a in companies])
    total_delta = sum([a.invoice_delta for a in companies])
    context = {'object_list':companies,
               'total_length':total_length,
               'total_price':total_price,
               'total_count':total_count,
               'total_building_price':total_building_price,
               'total_lector_price':total_lector_price,
               'total_delta':total_delta,
               'form': form,
               }
    return render_to_response('reports/company_added_value.html', RequestContext(request, context))
