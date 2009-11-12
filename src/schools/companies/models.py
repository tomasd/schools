# -*- coding: utf-8 -*-
from collections import defaultdict
from decimal import Decimal
from django.db import models
from django.db.models import permalink

class CompanyManager(models.Manager):
    def invoice(self, start, end, companies=[]):
        from schools.students.models import Student
        from schools.courses.models import LessonAttendee, CourseMember
        
        lesson_attendees = defaultdict(list)
        _attendees = LessonAttendee.objects.filter(lesson__real_end__range=(start, end))
        if companies: _attendees = _attendees.filter(course_member__student__company__in=companies)
        for attendee in _attendees.select_related('lesson'):
            lesson_attendees[attendee.course_member].append(attendee)

        course_members = defaultdict(list)
        _members = CourseMember.objects.filter(lessonattendee__lesson__real_end__range=(start, end))
        if companies: _members = _members.filter(student__company__in=companies)
        for course_member in _members.distinct():
            course_member.invoice_attendees = lesson_attendees[course_member]
            course_member.invoice_price = sum([a.course_member_price for a in lesson_attendees[course_member]])
            course_member.invoice_length = sum([a.lesson.real_minutes_length for a in lesson_attendees[course_member]])
            course_member.invoice_count = len(lesson_attendees[course_member])
            course_members[course_member.student].append(course_member)
        
        students_list = Student.objects.filter(coursemember__lessonattendee__lesson__real_end__range=(start, end)).distinct()
        if companies: students_list = students_list.filter(company__in=companies)
        students = defaultdict(list)
        for student in students_list:
            student.invoice_course_members = course_members[student]
            student.invoice_price = sum([a.invoice_price for a in course_members[student]])
            student.invoice_length = sum([a.invoice_length for a in course_members[student]])
            student.invoice_count = sum([a.invoice_count for a in course_members[student]])
            students[student.company].append(student)

        if not companies:
            companies = list(Company.objects.all())
        for company in companies:
            company.invoice_students = students[company]
            company.invoice_price = sum([a.invoice_price for a in students[company]])
            company.invoice_length = sum([a.invoice_length for a in students[company]])
            company.invoice_count = sum([a.invoice_count for a in students[company]])
            
        return companies

class Subcount(object):
    def __init__(self, course):
        super(Subcount, self).__init__()
        self.course = course
        self.length = 0
        self.price = Decimal(0)
        
class LectorManager(models.Manager):
    def lesson_analysis(self, start, end):
        from schools.courses.models import Lesson
        from schools.lectors.models import Lector
        
        lessons = Lesson.objects.filter(real_end__range=(start, end))
        
        lector_lessons = defaultdict(dict)
        
        for lesson in lessons:
            if lesson.course not in lector_lessons[lesson.real_lector]:
                lector_lessons[lesson.real_lector][lesson.course] = Subcount(lesson.course)
            subcount = lector_lessons[lesson.real_lector][lesson.course]
            subcount.length += lesson.real_minutes_length
            subcount.price += lesson.real_lector_price
            
        lectors = Lector.objects.all() #@UndefinedVariable
        for lector in lectors:
            lector.analysis_courses = lector_lessons[lector].values()
            lector.analysis_length = sum([subcount.length 
                                          for subcount in lector_lessons[lector].values() ])
            lector.analysis_price = sum([subcount.price 
                                          for subcount in lector_lessons[lector].values() ])
        return lectors

# Create your models here.
class Company(models.Model):
    objects = CompanyManager()
    name = models.CharField(max_length=100)
    
    ico = models.CharField(max_length=20, null=True, blank=True)
    dic = models.CharField(max_length=20, null=True, blank=True)
    ic_dph = models.CharField(max_length=20, null=True, blank=True)
    
    street = models.CharField(max_length=100, null=True, blank=True)
    postal = models.CharField(max_length=5, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    
    phone = models.CharField(max_length=30, null=True, blank=True)
    mobile = models.CharField(max_length=30, null=True, blank=True)
    fax = models.CharField(max_length=30, null=True, blank=True)
    www = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name
    
    @permalink
    def get_absolute_url(self):
        return ('companies_company_update', None, {'object_id':str(self.pk)})