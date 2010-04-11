# -*- coding: utf-8 -*-
from book_stock.models import BookDelivery
from collections import defaultdict
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import permalink, signals
from schools import fix_date_boundaries

class StudentManager(models.Manager):
    def book_invoice(self, start, end, companies=None):
        student_content_type = ContentType.objects.get_for_model(Student)
        deliveries = BookDelivery.objects.filter(person_type=student_content_type, 
                                                 delivered__range=(start,end))
        deliveries = [a for a in deliveries if companies is None or a.person.company in companies]
        students = set([a.person for a in deliveries])
        students = dict([(a,a) for a in students])
        for student in students:
            student.book_deliveries = []
        for delivery in deliveries:
            students[delivery.person].book_deliveries.append(delivery)
            
        for student in students:
            student.book_deliveries_sum = sum(a.price for a in student.book_deliveries)
        return students
                 
        
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
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
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
    
    @permalink
    def get_set_password_url(self):    
        return ('students_student_set_password', None, {'object_id':str(self.pk)})
    
    @permalink
    def get_bookorders_url(self):    
        return ('students_student_book_orders', None, {'object_id':str(self.pk)})
    
    @permalink
    def get_books_url(self):
        return ('students_student_books', None, {'object_id':str(self.pk)})
    
    @property
    def address(self):
        return '%s, %s %s' % (self.street, self.postal, self.town)