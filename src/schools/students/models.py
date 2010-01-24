# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import permalink
from collections import defaultdict
from schools import fix_date_boundaries

class StudentManager(models.Manager):
    def invoice(self, start, end, companies=None):
        from schools.courses.models import CourseMember
        
        course_members = CourseMember.objects.invoice(start, end, companies)
        
        students_list = Student.objects.filter(coursemember__lessonattendee__lesson__real_end__range=(start, fix_date_boundaries(end))).distinct()
        if companies is not None: students_list = students_list.filter(company__in=companies)
        students = defaultdict(list)
        for student in students_list:
            student.invoice_course_members = course_members[student]
            student.invoice_price = sum([a.invoice_price for a in course_members[student]])
            student.invoice_length = sum([a.invoice_length for a in course_members[student]])
            student.invoice_count = sum([a.invoice_count for a in course_members[student]])
            students[student.company].append(student)
            
        return students

class Student(models.Model):
    objects = StudentManager()
    from schools.companies.models import Company
    from django.contrib.auth.models import User
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    title = models.CharField(max_length=10, null=True, blank=True)
    company = models.ForeignKey(Company, null=True, blank=True)
    
    street = models.CharField(max_length=100, null=True, blank=True)
    postal = models.CharField(max_length=5, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    
    phone = models.CharField(max_length=30, null=True, blank=True)
    mobile = models.CharField(max_length=30, null=True, blank=True)
    fax = models.CharField(max_length=30, null=True, blank=True)
    www = models.URLField(null=True, blank=True,verify_exists=False)
    email = models.EmailField(null=True, blank=True)
    
    user = models.OneToOneField(User, null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name=u'študent'
        verbose_name_plural=u'študenti'
    
    def __unicode__(self):
        if self.title:
            return '%s, %s %s' % (self.last_name, self.first_name, self.title)
        return '%s, %s' % (self.last_name, self.first_name)
    
    @permalink
    def get_absolute_url(self):    
        return ('students_student_update', None, {'object_id':str(self.pk)})
    
    @permalink
    def get_courses_url(self):    
        return ('students_student_courses', None, {'object_id':str(self.pk)})

    @permalink
    def get_delete_url(self):    
        return ('students_student_delete', None, {'object_id':str(self.pk)})
    
    @property
    def address(self):
        return '%s, %s %s' % (self.street, self.postal, self.town)