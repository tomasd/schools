# -*- coding: utf-8 -*-
from collections import defaultdict
from django.db import models
from django.db.models import permalink

class StudentManager(models.Manager):
    def invoice(self, company, start, end):
        from schools.courses.models import LessonAttendee, CourseMember
        lesson_attendees = defaultdict(list)
        for attendee in LessonAttendee.objects.filter(course_member__student__company=company, lesson__real_end__range=(start, end)).select_related('lesson'):
            lesson_attendees[attendee.course_member].append(attendee)
            
        course_members = defaultdict(list)
        for course_member in CourseMember.objects.filter(student__company=company, lessonattendee__lesson__real_end__range=(start, end)).distinct():
            course_member.invoice_attendees = lesson_attendees[course_member]
            course_member.invoice_price = sum([a.course_member_price for a in lesson_attendees[course_member]])
            course_member.invoice_length = sum([a.lesson.real_minutes_length for a in lesson_attendees[course_member]])
            course_member.invoice_count = len(lesson_attendees[course_member])
            course_members[course_member.student].append(course_member)
        
        students = Student.objects.filter(company=company, coursemember__lessonattendee__lesson__real_end__range=(start, end)).distinct()
        for student in students:
            student.invoice_course_members = course_members[student]
            student.invoice_price = sum([a.invoice_price for a in course_members[student]])
            student.invoice_length = sum([a.invoice_length for a in course_members[student]])
            student.invoice_count = sum([a.invoice_count for a in course_members[student]])
        return students


# Create your models here.
class Student(models.Model):
    objects = StudentManager()
    from schools.companies.models import Company
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
    www = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        if self.title:
            return '%s, %s %s' % (self.last_name, self.first_name, self.title)
        return '%s, %s' % (self.last_name, self.first_name)
    
    @permalink
    def get_absolute_url(self):    
        return ('students_student_update', None, {'object_id':str(self.pk)})
