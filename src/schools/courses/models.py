# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import permalink

# Create your models here.
class Course(models.Model):
    from django.contrib.auth.models import User
    from schools.lectors.models import Lector
#    slug = models.SlugField(unique=True)
    responsible = models.ForeignKey(User)
    lector = models.ForeignKey(Lector)
    
    name = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
 
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name
 
    @permalink
    def get_absolute_url(self):
        return ('courses_course_update', None, {'object_id':str(self.pk)})
 
    @permalink
    def get_coursemembers_url(self):
        return ('courses_coursemember_list', None, {'course_id':str(self.pk)})
    
    @permalink
    def get_expensegroups_url(self):
        return ('courses_expensegroup_list', None, {'course_id':str(self.pk)})
    
class CourseMember(models.Model):
    from schools.students.models import Student
    course = models.ForeignKey('Course')
    student = models.ForeignKey(Student)
    
    start = models.DateField()
    end = models.DateField(null=True, blank=True)
    
    expense_group = models.ForeignKey('ExpenseGroup')
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return unicode(self.student)
    
    def create_individual_expense_group(self, price):
        expense_group = ExpenseGroup(course=self.course, name=unicode(self.student))
        expense_group.save()
        expense_group.expensegroupprice_set.create(price=price, start=self.start)
        self.expense_group = expense_group
        return expense_group
    
    @permalink
    def get_absolute_url(self):
        return ('courses_coursemember_update', None, {'course_id':str(self.course.pk), 'object_id':str(self.pk)})
            
class Lesson(models.Model):
    from schools.buildings.models import Classroom
    course = models.ForeignKey('Course')
    classroom = models.ForeignKey(Classroom)
    
    start = models.DateTimeField()
    end = models.DateTimeField()
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        start_format = '%d.%m.%Y %H:%M'
        end_format = '%H:%M' if self.end.date() == self.start.date() else start_format
        
        return '%s: %s - %s' % (self.classroom,
                                format(self.start, start_format),
                                format(self.end, end_format))
        
    def create_attendance_list(self):
        try:
            return self.attendancelist
        except AttendanceList.DoesNotExist:
            return AttendanceList(lesson=self,
                              classroom=self.classroom,
                              lector=self.course.lector,
                              start=self.start, end=self.end)
    
    
class AttendanceList(models.Model):
    from schools.lectors.models import Lector
    from schools.buildings.models import Classroom
    classroom = models.ForeignKey(Classroom)
    lesson = models.OneToOneField('Lesson')
    lector = models.ForeignKey(Lector)
    
    lector_price = models.DecimalField(max_digits=10, decimal_places=2)
    start = models.DateTimeField()
    end = models.DateTimeField()
    
    content = models.TextField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
        
    def new_course_members(self):
        course_members = CourseMember.objects.exclude(lessonattendee=self)
        return [LessonAttendee(attendance_list=self, course_member=a, present=False) for a in course_members]
           
    
    
class LessonAttendee(models.Model):
    attendance_list = models.ForeignKey('AttendanceList')
    course_member = models.ForeignKey('CourseMember')
    
    present = models.BooleanField(default=True)
    course_member_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
class ExpenseGroup(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey('Course')
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name
    
    @permalink
    def get_absolute_url(self):
        return ('courses_expensegroup_update', None, {'course_id':str(self.course.pk), 
                                                      'object_id':str(self.pk)})
    
class ExpenseGroupPrice(models.Model):
    expense_group = models.ForeignKey('ExpenseGroup')
    
    start = models.DateField()
    end = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)