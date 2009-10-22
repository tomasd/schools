# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import permalink, signals
from django.db.models.query_utils import Q
import django.dispatch
from collections import defaultdict

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
    
    @permalink
    def get_lessons_url(self):
        return ('courses_lesson_list', None, {'course_id':str(self.pk)})

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
        return unicode(self.student) + str(self.course.pk)
    
    def create_individual_expense_group(self, price):
        expense_group = ExpenseGroup(course=self.course, name=unicode(self.student))
        expense_group.save()
        expense_group.expensegroupprice_set.create(price=price, start=self.start)
        self.expense_group = expense_group
        return expense_group
    
    @permalink
    def get_absolute_url(self):
        return ('courses_coursemember_update', None, {'course_id':str(self.course.pk), 'object_id':str(self.pk)})


lesson_assign_attendees = django.dispatch.Signal(providing_args=["lesson"])
def create_lesson_attendees(sender, *args, **kwargs):
    lesson = kwargs['lesson']
    course_members = lesson.course.coursemember_set.filter(Q(end__isnull=True) | Q(end__gte=lesson.start), start__lte=lesson.end)
    lesson_members = [a.course_member for a in lesson.lessonattendee_set.all()]
    course_members = filter(lambda member:member not in lesson_members, course_members)
    lesson.lessonattendee_set = [LessonAttendee(course_member=a) for a in course_members] 
    
lesson_assign_attendees.connect(create_lesson_attendees)      
class Lesson(models.Model):
    from schools.buildings.models import Classroom
    from schools.lectors.models import Lector
    course = models.ForeignKey('Course')
    classroom = models.ForeignKey(Classroom, related_name='plannedlessons_set')
    
    start = models.DateTimeField()
    end = models.DateTimeField()
    
    realized = models.BooleanField()
    real_classroom = models.ForeignKey(Classroom, null=True, related_name='reallessons_set')
    real_lector = models.ForeignKey(Lector, null=True)
    real_lector_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    real_start = models.DateTimeField(null=True)
    real_minutes_length = models.IntegerField(null=True, editable=False)
    real_end = models.DateTimeField(null=True)
    real_content = models.TextField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        start_format = '%d.%m.%Y %H:%M'
        end_format = '%H:%M' if self.end.date() == self.start.date() else start_format
        
        start, end = self.start, self.end
        if self.realized:
            start, end = self.real_start, self.real_end
        return '%s: %s - %s' % (self.classroom,
                                format(start, start_format),
                                format(end, end_format))
    
    @permalink
    def get_absolute_url(self):
        return ('courses_lesson_update', None, {'course_id':str(self.course.pk), 'object_id':str(self.pk)})
    
    @permalink
    def get_attendance_url(self):
        return ('courses_lesson_attendance', None, {'course_id':str(self.course.pk), 'object_id':str(self.pk)})
        
    def fill_attendance(self):
        self.realized = True
        self.real_start = self.start
        self.real_end = self.end
        self.real_classroom = self.classroom
        self.real_lector = self.course.lector
        return self

def calculate_price(hour_rate, delta):    
    return hour_rate * delta_to_minutes(delta) / 60
    
def delta_to_minutes(delta):
    return delta.days * 24*60 + delta.seconds // 60
    
def lector_price(sender, *args, **kwargs):
    lesson = kwargs['instance']
    if lesson.realized:
        contract = lesson.real_lector.contract_set.get(start__lte=lesson.real_end, end__gte=lesson.real_start)
        hour_rates = [a for a in contract.hourrate_set.all() if a.course == lesson.course]
        hour_rate = hour_rates[-1].hour_rate if hour_rates else contract.hour_rate
        lesson.real_lector_price = calculate_price(hour_rate, lesson.real_end - lesson.real_start)
signals.pre_save.connect(lector_price, sender=Lesson)        

def lesson_length(sender, *args, **kwargs):
    '''
        Set real lesson minutes length.
    '''
    lesson = kwargs['instance']
    if lesson.realized:
        lesson.real_minutes_length = delta_to_minutes(lesson.real_end - lesson.real_start)
signals.pre_save.connect(lesson_length, sender=Lesson)

def course_member_price(sender, *args, **kwargs):
    lesson = kwargs['instance']
    if lesson.realized:
        expense_groups = defaultdict(list)
        for attendee in lesson.lessonattendee_set.all():
            expense_groups[attendee.course_member.expense_group].append(attendee)
        
        for expense_group, attendees in expense_groups.items():
            expense_group_prices = expense_group.expensegroupprice_set.filter(Q(end__isnull=True)|Q(end__gte=lesson.real_start), start__lte=lesson.real_end)
            hour_rate = list(expense_group_prices)[-1]
            price = calculate_price(hour_rate.price, lesson.real_end - lesson.real_start)
            for attendee in attendees:
                attendee.course_member_price = price / len(attendees)
                attendee.save()
                
signals.post_save.connect(course_member_price, sender=Lesson)

#class AttendanceList(models.Model):
#    from schools.lectors.models import Lector
#    from schools.buildings.models import Classroom
#    classroom = models.ForeignKey(Classroom)
#    lesson = models.OneToOneField('Lesson')
#    lector = models.ForeignKey(Lector)
#    
#    lector_price = models.DecimalField(max_digits=10, decimal_places=2)
#    start = models.DateTimeField()
#    end = models.DateTimeField()
#    
#    content = models.TextField(null=True, blank=True)
#    
#    created = models.DateTimeField(auto_now_add=True)
#    updated = models.DateTimeField(auto_now=True)
#    
#        
#    def new_course_members(self):
#        course_members = CourseMember.objects.exclude(lessonattendee=self)
#        return [LessonAttendee(attendance_list=self, course_member=a, present=False) for a in course_members]
#           
    
    
class LessonAttendee(models.Model):
    lesson = models.ForeignKey('Lesson')
    course_member = models.ForeignKey('CourseMember')
    
    present = models.BooleanField(default=False)
    course_member_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
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