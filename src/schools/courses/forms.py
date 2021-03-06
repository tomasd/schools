# -*- coding: utf-8 -*-
from datepicker.widgets import SplitDatePickerTimePickerWidget
from django import forms
from django.forms.util import ValidationError
from django.forms.widgets import HiddenInput, Select, DateTimeInput, Widget, \
    CheckboxSelectMultiple
from django.utils.translation import ugettext
from schools.buildings import classroom_buildings
from schools.buildings.models import Classroom, Building
from schools.courses.models import Course, CourseMember, ExpenseGroup, Lesson, \
    LessonAttendee, ReasonForNotRealizing, lesson_assign_attendees,\
    format_time_range
from schools.lectors.models import Lector
from datetime import timedelta


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
    
class CourseMemberCreateForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    expense_group = forms.ModelChoiceField(queryset=ExpenseGroup.objects.all(), required=False)
    expense_group_name = forms.CharField(max_length=100, required=False)
    expense_group_price = forms.DecimalField(min_value=0, required=False)
    class Meta:
        model = CourseMember
        
    def limit_to_course(self, course):
        self.fields['expense_group'].queryset = self.fields['expense_group'].queryset.filter(course=course)
        
    def clean(self):
        cleaned_data = self.cleaned_data
        if not (cleaned_data['expense_group'] or (cleaned_data['expense_group_name'] and cleaned_data['expense_group_price'])):
            raise ValidationError(ugettext(u'Choose expense group or fill in expense group name and price.'))
        
        if not cleaned_data['expense_group']:
            expense_group = ExpenseGroup(course=self.cleaned_data['course'], name=self.cleaned_data['expense_group_name'])
            expense_group.save()
            expense_group.expensegroupprice_set.create(start=self.cleaned_data['start'], price=self.cleaned_data['expense_group_price'])
            cleaned_data['expense_group'] = expense_group
        return cleaned_data
    
class CourseMemberForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    class Meta:
        model = CourseMember
        exclude = ('student',)
    def limit_to_course(self, course):
        self.fields['expense_group'].queryset = self.fields['expense_group'].queryset.filter(course=course) 
        
class ExpenseGroupForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    class Meta:
        model = ExpenseGroup        

def validate_overlapping_lessons(start, end, classroom, matching_lessons):
    if matching_lessons:
        times = [format_time_range(a.start,a.end) for a in matching_lessons]
        p = (classroom, format_time_range(start, end), ', '.join(times))
        raise ValidationError(ugettext(u'Učebňa %s je v čase %s už obsadená pre časy: %s') % p)
class LessonPlanForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput(attrs={'class':'course'}))
    classroom = forms.ModelChoiceField(queryset=Classroom.objects.all(), widget=Select(attrs={'class':'classroom'}))
    start = forms.DateTimeField(widget=SplitDatePickerTimePickerWidget(attrs={'class':'start'}))
    end = forms.DateTimeField(widget=SplitDatePickerTimePickerWidget(attrs={'class':'end'}))
    class Meta:
        model = Lesson
        fields = ('course', 'classroom', 'start', 'end',)
        
    def __init__(self, *args, **kwargs):
        super(LessonPlanForm, self).__init__(*args, **kwargs)
        classroom_buildings(self.fields['classroom'])
        self.fields['classroom'].required=True
        
    def clean(self):
        data = self.cleaned_data
        if 'classroom' in data and 'start' in data and 'end' in data:
            matching_lessons = Lesson.objects.matching_lessons(classroom=data['classroom'], 
                                            start=data['start'], end=data['end'])
            validate_overlapping_lessons(data['start'], data['end'], data['classroom'], matching_lessons)
        return data
        
class LessonRealizedForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    realized = forms.BooleanField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(LessonRealizedForm, self).__init__(*args, **kwargs)
        classroom_buildings(self.fields['real_classroom'])
        
    class Meta:
        model = Lesson
        fields = ('realized', 'real_classroom', 'real_lector', 'real_start', 'real_end', 'real_content', 'course', 'reason_of_not_realizing')

class LessonRealizedForm1(forms.Form):
    lesson = forms.ModelChoiceField(queryset=Lesson.objects.all(), widget=HiddenInput)
    real_classroom = forms.ModelChoiceField(queryset=Classroom.objects.all())
    real_lector = forms.ModelChoiceField(queryset=Lector.objects.all())
    real_start = forms.DateTimeField()
    real_end = forms.DateTimeField()
    real_content = forms.CharField(widget=forms.Textarea)
    reason_of_not_realizing = forms.ModelChoiceField(queryset=ReasonForNotRealizing.objects.all(), required=False)
    lesson_attendees = forms.ModelMultipleChoiceField(queryset=LessonAttendee.objects.all(), widget=CheckboxSelectMultiple, required=False)
    
    def __init__(self, instance=None, *args, **kwargs):
        if instance is None:
            instance = Lesson.objects.get(pk=kwargs['initial']['lesson'])
        lesson = instance
        self.instance = instance
        lesson_assign_attendees.send(sender=self, lesson=lesson)
        
        initial = kwargs.get('initial', {}); kwargs['initial'] = initial
        if 'real_classroom' not in initial: 
            initial['real_classroom'] = instance.real_classroom.pk if instance.realized else instance.classroom.pk
        if 'real_lector' not in initial: 
            initial['real_lector'] = instance.real_lector.pk if instance.realized else instance.course.lector.pk
        if 'real_content' not in initial and instance.realized: 
            initial['real_content'] = instance.real_content
        if 'real_start' not in initial: 
            initial['real_start'] = instance.real_start if instance.realized else instance.start
        if 'real_end' not in initial: 
            initial['real_end'] = instance.real_end if instance.realized else instance.end
        if 'lesson_attendees' not in initial: 
            initial['lesson_attendees'] = [a.pk for a in instance.lessonattendee_set.all() if a.present]
        
        super(LessonRealizedForm1, self).__init__(*args, **kwargs)
        self.fields['lesson'].initial = lesson.pk
        classroom_buildings(self.fields['real_classroom'])
        self.fields['lesson_attendees'].queryset = lesson.lessonattendee_set.all() 
        
    def save(self):
        lesson = self.cleaned_data['lesson']
        fields = [(key, value) for key, value in self.cleaned_data.items() if key not in ('lesson', 'lesson_attendees')]
        for name, value in fields:
            setattr(lesson, name, value)
        lesson.realized = True
        lesson.save()
        for lesson_attendee in lesson.lessonattendee_set.all():
            if lesson_attendee in self.cleaned_data['lesson_attendees']:
                lesson_attendee.present = True; lesson_attendee.save()
            else:
                lesson_attendee.present = False; lesson_attendee.save()
                  
        return lesson

class LessonAttendeeForm(forms.ModelForm):
    class Meta:
        model = LessonAttendee
        exclude = ('course_member_price',)
    def limit_to_course(self, course):
        self.fields['course_member'].queryset = self.fields['course_member'].queryset.filter(course=course)
        
class ChooseClassroomForm(forms.Form):
    classroom = forms.ModelChoiceField(queryset=Classroom.objects.all())

    def __init__(self, *args, **kwargs):
        super(ChooseClassroomForm, self).__init__(*args, **kwargs)
        classroom_buildings(self.fields['classroom'])
    
class ReplanLessonForm(forms.ModelForm):
    '''
        Plan lesson on the other time.
    '''
    start = forms.DateTimeField(widget=DateTimeInput)
    end = forms.DateTimeField(widget=DateTimeInput)
    class Meta:
        model = Lesson
        fields = ('start', 'end')
        
class LessonSearchForm(forms.Form):
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)
    realized = forms.NullBooleanField(required=False)
    lector = forms.ModelChoiceField(queryset=Lector.objects.all(), required=False)
    building = forms.ModelChoiceField(queryset=Building.objects.all(), required=False)
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=False)
    classroom = forms.ModelChoiceField(queryset=Classroom.objects.all(), required=False)    
    
    def __init__(self, *args, **kwargs):
        date_required = kwargs.get('date_required', False)
        if 'date_required' in kwargs:
            kwargs.pop('date_required')
        
        super(LessonSearchForm, self).__init__(*args, **kwargs)
        classroom_buildings(self.fields['classroom'])

        self.fields['start'].required = date_required
        self.fields['end'].required = date_required
        
    def clean(self):
        data = self.cleaned_data
        
        if not data.get('start') or not data.get('end') or data.get('end') > data.get('start') + timedelta(days=31) :
            raise ValidationError(ugettext(u'Môžete zadať maximálne mesačné obdobie'))
        return data