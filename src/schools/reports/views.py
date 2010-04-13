# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from pyjasper.client import JasperGenerator
from schools.companies.models import Company
from schools.courses.models import Course, LessonAttendee
from schools.lectors.models import Lector
from schools.reports.forms import InvoiceForm, LessonAnalysisForm, \
    LessonPlanForm, CompanyAddedValueForm
from xml.etree import ElementTree as ET
from django.template.defaultfilters import yesno
from django.utils.translation import ugettext
from django.http import HttpResponse
from django.utils import dateformat

class InvoicePdfGenerator(JasperGenerator):
    '''
        Jasper generator for invoices.
    '''
    def __init__(self):
        super(InvoicePdfGenerator, self).__init__()
        self.reportname = 'reports/invoice.jrxml'
        print open(self.reportname).read()
        self.xpath = '/invoice/lesson'
        self.root = ET.Element('invoice')
    def generate_xml(self, (lesson_attendees, from_, to_)): 
        """Generates the XML File used by Jasperreports""" 
        self.root.attrib['from'] = dateformat.format(from_, 'd.m.Y')
        self.root.attrib['to'] = dateformat.format(to_, 'd.m.Y')
        for lesson_attendee in lesson_attendees: 
            lesson = ET.SubElement(self.root, 'lesson') 
            course_member =lesson_attendee.course_member
            course = course_member.course
            student = course_member.student
            company = student.company
            ET.SubElement(lesson, 'student').text = unicode(student.pk)
            ET.SubElement(lesson, 'company').text = unicode(company.pk)
            ET.SubElement(lesson, 'course').text = unicode(course.pk)
            ET.SubElement(lesson, 'companyName').text = unicode(company)
            ET.SubElement(lesson, 'studentName').text = unicode(student)
            ET.SubElement(lesson, 'courseName').text = unicode(course)
            ET.SubElement(lesson, 'lessonDate').text = unicode(lesson_attendee.lesson)
            ET.SubElement(lesson, 'length').text = unicode(lesson_attendee.lesson.real_minutes_length)
            ET.SubElement(lesson, 'price').text = unicode(lesson_attendee.course_member_price)
            ET.SubElement(lesson, 'present').text = yesno(lesson_attendee.present, ugettext(u'áno,nie'))
            
        return self.root

def invoice_pdf(request, companies=None):
    if companies is None: companies = Company.objects.all()
    form = InvoiceForm(companies, request.GET)
    if form.is_valid():
        lesson_attendees = LessonAttendee.objects.filter(lesson__real_end__range=(form.cleaned_data['start'], form.cleaned_data['end']))
        lesson_attendees = lesson_attendees.filter(course_member__student__company__in=form.cleaned_data['companies'])                
        pdf = InvoicePdfGenerator().generate((lesson_attendees.all(), form.cleaned_data['start'], form.cleaned_data['end']))
        return HttpResponse(pdf, 'application/pdf')
    else:
        return HttpResponse(form.errors.as_ul)

def invoice(request, companies=None, template='reports/invoice.html', extra_context=None, empty_when_no_companies=False):
    acompanies = companies
    if companies is None: companies = Company.objects.all()
    if request.GET:
        form = InvoiceForm(companies, request.GET)
        if form.is_valid():
            invoice_companies = set(form.cleaned_data['companies'])
            if acompanies is None: 
                invoice_companies = Company.objects.all() if not form.cleaned_data['companies'] else set(form.cleaned_data['companies'])
            else:
                invoice_companies &= set(acompanies)
            ret_companies = Company.objects.invoice(companies=invoice_companies,
                                                start=form.cleaned_data['start'],
                                                end=form.cleaned_data['end'], )
            total_length = sum([a.invoice_length for a in ret_companies])
            total_price = sum([a.invoice_price for a in ret_companies])
            total_count = sum([a.invoice_count for a in ret_companies])
            context = {'object_list':ret_companies,
                       'total_length':total_length,
                       'total_price':total_price,
                       'total_count':total_count,
                       'show_students':form.cleaned_data['show_students'],
                       }
        else:
            context = { 'nolist':True, 'object_list':companies}
    else:
        context = { 'nolist':True, 'object_list':companies}
        form = InvoiceForm(companies=companies, initial={'companies':','.join(str(a.pk) for a in companies)})
    context['form'] = form
    if extra_context:
        context.update(extra_context)
    return render_to_response(template, RequestContext(request, context))

def book_invoice_dict(request, companies, acompanies):
    form = InvoiceForm(companies, request.GET)
    if form.is_valid():
        invoice_companies = set(form.cleaned_data['companies'])
        if acompanies is None: 
            invoice_companies = Company.objects.all() if not form.cleaned_data['companies'] else set(form.cleaned_data['companies'])
        else:
            invoice_companies &= set(acompanies)
        ret_companies = Company.objects.book_invoice(companies=invoice_companies,
                                            start=form.cleaned_data['start'],
                                            end=form.cleaned_data['end'], )
        total_book_invoice_sum = sum([a.book_invoice_students_sum for a in ret_companies])
        context = {'object_list':ret_companies,
                   'total_book_invoice_sum':total_book_invoice_sum,
                   'show_students':form.cleaned_data['show_students'],
                   }
    else:
        context = { 'nolist':True, 'object_list':companies}
    return context
        
def book_invoice(request, companies=None, template='reports/book_invoice.html', extra_context=None, empty_when_no_companies=False):
    acompanies = companies
    if companies is None: companies = Company.objects.all()
    if request.GET:
        context = book_invoice_dict(request, companies, acompanies)
    else:
        context = { 'nolist':True, 'object_list':companies}
        form = InvoiceForm(companies=companies, initial={'companies':','.join(str(a.pk) for a in companies)})
    context['form'] = form
    if extra_context:
        context.update(extra_context)
    return render_to_response(template, RequestContext(request, context))

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
        form = InvoiceForm(Company.objects.all())
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
