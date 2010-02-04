# -*- coding: utf-8 -*-
from collections import defaultdict
from decimal import Decimal
from django.db import models
from django.db.models import permalink, signals

class CompanyManager(models.Manager):
    def invoice(self, start, end, companies=None):
        from schools.students.models import Student
        
        students = Student.objects.invoice(start, end, companies)
        
        if companies is None:
            companies = list(Company.objects.all())
        for company in companies:
            company.invoice_students = students[company]
            company.invoice_price = sum([a.invoice_price for a in students[company]])
            company.invoice_length = sum([a.invoice_length for a in students[company]])
            company.invoice_count = sum([a.invoice_count for a in students[company]])
            
        return companies
    
    def added_value(self, start, end, companies=[]):
        from schools.students.models import Student
#        platca, kurzohodiny, cena vyučovania, cena budovy, lektorské, rozdiel
        students = Student.objects.invoice(start, end, companies)
        building_attendees = defaultdict(list)
        lesson_attendees = defaultdict(list)
        
        for student_list in students.values():
            for student in student_list:
                student.invoice_building_price = Decimal(0)
                student.invoice_lector_price = Decimal(0)
                student.invoice_delta = Decimal(0)
                for course_member in student.invoice_course_members:
                    course_member.invoice_building_price = Decimal(0)
                    course_member.invoice_lector_price = Decimal(0)
                    course_member.invoice_delta = Decimal(0)
                    course_member.student = student
                    for lesson_attendee in course_member.invoice_attendees:
                        building_attendees[lesson_attendee.lesson.real_classroom.building].append(lesson_attendee)
                        lesson_attendees[lesson_attendee.lesson].append(lesson_attendee)
                        lesson_attendee.course_member = course_member
                        
        for building, attendees in building_attendees.items():
            building_price = building.building_price_for(start, end)
            price_per_attendee = building_price / Decimal(len(attendees))
            for lesson_attendee in attendees:
                #building
                lesson_attendee.invoice_building_price = price_per_attendee
                lesson_attendee.course_member.invoice_building_price += price_per_attendee
                lesson_attendee.course_member.student.invoice_building_price += price_per_attendee
                
                # lector
                lesson_attendee.invoice_lector_price = lesson_attendee.lesson.real_lector_price / len(lesson_attendees[lesson_attendee.lesson])
                lesson_attendee.course_member.invoice_lector_price += lesson_attendee.invoice_lector_price
                lesson_attendee.course_member.student.invoice_lector_price += lesson_attendee.invoice_lector_price
                
                # delta
                lesson_attendee.invoice_delta = lesson_attendee.course_member_price - lesson_attendee.invoice_building_price - lesson_attendee.invoice_lector_price
                lesson_attendee.course_member.invoice_delta += lesson_attendee.invoice_delta
                lesson_attendee.course_member.student.invoice_delta += lesson_attendee.invoice_delta 

        if not companies:
            companies = list(Company.objects.all())
        for company in companies:
            company.invoice_students = students[company]
            company.invoice_price = sum([a.invoice_price for a in students[company]])
            company.invoice_length = sum([a.invoice_length for a in students[company]])
            company.invoice_count = sum([a.invoice_count for a in students[company]])
            company.invoice_building_price = sum([a.invoice_building_price for a in students[company]])
            company.invoice_lector_price = sum([a.invoice_lector_price for a in students[company]])
            company.invoice_delta = sum([a.invoice_delta for a in students[company]])
        
        return companies
                    

class Subcount(object):
    def __init__(self, course):
        super(Subcount, self).__init__()
        self.course = course
        self.length = 0
        self.price = Decimal(0)
        

# Create your models here.
class Company(models.Model):
    from django.contrib.auth.models import User
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
    
    users = models.ManyToManyField(User)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name=u'firma'
        verbose_name_plural=u'firmy'
        
        permissions = (
            ("can_see_invoice", ("Can see invoice")),
            ("can_see_added_value", ("Can see added value")),
        )

    
    def __unicode__(self):
        return self.name
    
    @permalink
    def get_absolute_url(self):
        return ('companies_company_update', None, {'object_id':str(self.pk)})
    
    @permalink
    def get_students_url(self):
        return ('companies_company_students', None, {'object_id':str(self.pk)})
    
    @permalink
    def get_delete_url(self):
        return ('companies_company_delete', None, {'object_id':str(self.pk)})
    
    def can_remove(self):
        return self.student_set.count() == 0
    
