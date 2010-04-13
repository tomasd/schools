# -*- coding: utf-8 -*-
from collections import defaultdict
from django.conf import settings
from django.db import models
from django.db.models import permalink, signals
from django.db.models.query_utils import Q
from schools import fix_date_boundaries
import django.dispatch
from django.utils.dateformat import format

# Create your models here.

class CourseManager(models.Manager):
    def course_plan(self, start, end):
        class CoursePlan():
            def __init__(self, lessonhours, price):
                self.lesson_hours = lessonhours
                self.price = price
                
                
        lessons = Lesson.objects.filter(end__range=(start, fix_date_boundaries(end)))
        # kurz, plánované lekciohodiny, plánované kurzohodiny, plánovaná cena
        lesson_dict = defaultdict(list)
        
        for lesson in lessons:
            lesson_dict[lesson.course].append(lesson)
            
        for course, lessons_list in lesson_dict.items():
            lessonhours = sum([lesson.minutes_length for lesson in lessons_list])
            course_members = course.coursemember_set.filter(Q(end__isnull=True) | Q(end__gte=start), start__lt=fix_date_boundaries(end))
            price = sum([sum(course_member_price(lesson, course_members, lesson.start, lesson.end).values()) for lesson in lessons_list])
            
            course.course_plan = CoursePlan(lessonhours, price)
            
        return lesson_dict.keys()
            
class Course(models.Model):
    objects = CourseManager()
    from django.contrib.auth.models import User
    from schools.lectors.models import Lector
#    slug = models.SlugField(unique=True)
    responsible = models.ForeignKey(User)
    lector = models.ForeignKey(Lector)
    
    name = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=2,choices=settings.SCHOOL_LANGUAGES)
 
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name=u'kurz'
        verbose_name_plural=u'kurzy'
        
        permissions = (
            ("can_see_lesson_plan", ("Can see lesson plan")),
            ("can_see_lesson_analysis", ("Can see lesson analysis")),
        )

        
    def __unicode__(self):
        return self.name
 
    @permalink
    def get_absolute_url(self):
        return ('courses_course_update', None, {'object_id':str(self.pk)})
 
    @permalink
    def get_delete_url(self):
        return ('courses_course_delete', None, {'object_id':str(self.pk)})
 
    @permalink
    def get_coursemembers_url(self):
        return ('courses_coursemember_list', None, {'course_id':str(self.pk)})
    
    @permalink
    def get_expensegroups_url(self):
        return ('courses_expensegroup_list', None, {'course_id':str(self.pk)})
    
    @permalink
    def get_testing_url(self):
        return ('courses_course_test_result_list', None, {'course_id':str(self.pk)})
    
    @permalink
    def get_lessons_url(self):
        return ('courses_lesson_list', None, {'course_id':str(self.pk)})
    
    @permalink
    def get_attendance_url(self):
        return ('courses_course_lesson_attendance_list', None, {'course_id':str(self.pk)})


class CourseMemberManager(models.Manager):
    def invoice(self, start, end, companies=None):
        lesson_attendees = defaultdict(list)
        _attendees = LessonAttendee.objects.filter(lesson__real_end__range=(start, fix_date_boundaries(end)))
        if companies is not None: _attendees = _attendees.filter(course_member__student__company__in=companies)
        for attendee in _attendees.select_related('lesson'):
            lesson_attendees[attendee.course_member].append(attendee)

        course_members = defaultdict(list)
        _members = CourseMember.objects.filter(lessonattendee__lesson__real_end__range=(start, fix_date_boundaries(end)))
        if companies is not None: _members = _members.filter(student__company__in=companies)
        for course_member in _members.distinct():
            course_member.invoice_attendees = lesson_attendees[course_member]
            course_member.invoice_price = sum([a.course_member_price for a in lesson_attendees[course_member]])
            course_member.invoice_length = sum([a.lesson.real_minutes_length for a in lesson_attendees[course_member]])
            course_member.invoice_count = len(lesson_attendees[course_member])
            course_members[course_member.student].append(course_member)
        return course_members
    
class CourseMember(models.Model):
    objects = CourseMemberManager()
    from schools.students.models import Student
    course = models.ForeignKey('Course')
    student = models.ForeignKey(Student)
    
    start = models.DateField()
    end = models.DateField(null=True, blank=True)
    
    expense_group = models.ForeignKey('ExpenseGroup')
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name=u'účastnik kurzu'
        verbose_name_plural=u'účastníci kurzu'
        
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
    
    @permalink
    def get_delete_url(self):
        return ('courses_coursemember_delete', None, {'course_id':str(self.course.pk), 'object_id':str(self.pk)})

    def duration(self):
        start_format = 'd.m.Y'
        if self.end is None:
            return '%s - ' % format(self.start, start_format)
        return '%s - %s' % (format(self.start, start_format), format(self.end, start_format))
    
    def attendance(self):
        lessons = LessonAttendee.objects.filter(course_member=self)
        attended = len([filter(lambda a:a.present, lessons)])
        if not lessons:
            return 0
        return float(attended)/len(lessons)
    
lesson_assign_attendees = django.dispatch.Signal(providing_args=["lesson"])
def create_lesson_attendees(sender, *args, **kwargs):
    lesson = kwargs['lesson']
    course_members = lesson.course.coursemember_set.filter(Q(end__isnull=True) | Q(end__gte=lesson.start), start__lt=fix_date_boundaries(lesson.end))
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
    
    reason_of_not_realizing = models.ForeignKey('ReasonForNotRealizing', null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name=u'lekcia'
        verbose_name_plural=u'lekcie'
        
    def __unicode__(self):
        start_format = 'd.m.Y H:i'
        end_format = 'H:i' if self.end.date() == self.start.date() else start_format
        
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
    
    @property
    def minutes_length(self):
        return delta_to_minutes(self.end - self.start)

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

def lesson_attendee_price(sender, *args, **kwargs):
    lesson = kwargs['instance']
    update_lesson_price(lesson)
signals.post_save.connect(lesson_attendee_price, sender=Lesson)
                        
def course_member_price(lesson, course_members, start, end):
    expense_groups = defaultdict(list)
    for course_member in course_members:
        expense_groups[course_member.expense_group].append(course_member)
    
    course_members_dict = {}
    for expense_group, course_members in expense_groups.items():
        expense_group_prices = expense_group.expensegroupprice_set.filter(Q(end__isnull=True)|Q(end__gte=start), start__lt=fix_date_boundaries(end))
        hour_rate = list(expense_group_prices)[-1]
        price = calculate_price(hour_rate.price, end - start)
        for course_member in course_members:
            course_members_dict[course_member] = price / len(course_members)
    return course_members_dict

def update_lesson_price(lesson):
    if lesson.realized:
        attendees = lesson.lessonattendee_set.all()
        course_members = [a.course_member for a in attendees]
        member_price = course_member_price(lesson, course_members, lesson.real_start, lesson.real_end)
        
        for attendee in attendees:
            attendee.course_member_price = member_price[attendee.course_member]
            attendee.save()

class LessonAttendee(models.Model):
    lesson = models.ForeignKey('Lesson')
    course_member = models.ForeignKey('CourseMember')
    
    present = models.BooleanField(default=False)
    course_member_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name=u'Účastník lekcie'
        verbose_name_plural=u'Účastníci lekcie'
        
    def __unicode__(self):
        return unicode(self.course_member)
        
        
def lesson_attendee_price_update(sender, *args, **kwargs):
    lesson_attendee = kwargs['instance']
    update_lesson_price(lesson_attendee.lesson)
signals.pre_delete.connect(lesson_attendee_price_update, sender=LessonAttendee)
    
class ExpenseGroup(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey('Course')
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name=u'Nákladová skupina'
        verbose_name_plural=u'Nákladové skupiny'
        
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
    
    class Meta:
        verbose_name=u'Hodinová sadzba nákladovej skupiny'
        verbose_name_plural=u'Hodinové sazdby nákladovej skupiny'
        
        
class ReasonForNotRealizing(models.Model):
    name = models.CharField(max_length=200)
    
    class Meta:
        verbose_name=u'Dôvod nerealizovania'
        verbose_name_plural=u'Dôvody nerealizovania'
        
    def __unicode__(self):
        return self.name