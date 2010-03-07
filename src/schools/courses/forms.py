from datepicker.widgets import SplitDatePickerTimePickerWidget
from django import forms
from django.forms.util import ValidationError
from django.forms.widgets import HiddenInput, Select, DateTimeInput
from django.utils.translation import ugettext
from schools.buildings.models import Classroom, Building
from schools.courses.models import Course, CourseMember, ExpenseGroup, Lesson, \
    LessonAttendee
from schools.lectors.models import Lector


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

class LessonPlanForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput(attrs={'class':'course'}))
    classroom = forms.ModelChoiceField(queryset=Classroom.objects.all(), widget=Select(attrs={'class':'classroom'}))
    start = forms.DateTimeField(widget=SplitDatePickerTimePickerWidget(attrs={'class':'start'}))
    end = forms.DateTimeField(widget=SplitDatePickerTimePickerWidget(attrs={'class':'end'}))
    
    def __init__(self, *args, **kwargs):
        super(LessonPlanForm, self).__init__(*args, **kwargs)
        self.fields['classroom']._choices = [(unicode(a), [(b.pk, unicode(b)) for b in a.classroom_set.all()]) for a in Building.objects.all()]
        self.fields['classroom'].queryset = Classroom.objects.all()
        
    class Meta:
        model = Lesson
        fields = ('course', 'classroom', 'start', 'end',)
        
class LessonRealizedForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    realized = forms.BooleanField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(LessonRealizedForm, self).__init__(*args, **kwargs)
        self.fields['real_classroom']._choices = [(unicode(a), [(b.pk, unicode(b)) for b in a.classroom_set.all()]) for a in Building.objects.all()]
        self.fields['real_classroom'].queryset = Classroom.objects.all()
        
    class Meta:
        model = Lesson
        fields = ('realized', 'real_classroom', 'real_lector', 'real_start', 'real_end', 'real_content', 'course', 'reason_of_not_realizing')

class LessonAttendeeForm(forms.ModelForm):
    class Meta:
        model = LessonAttendee
        exclude = ('course_member_price', )
    def limit_to_course(self, course):
        self.fields['course_member'].queryset = self.fields['course_member'].queryset.filter(course=course)
        
class ChooseClassroomForm(forms.Form):
    classroom = forms.ModelChoiceField(queryset=Classroom.objects.all())

    def __init__(self, *args, **kwargs):
        super(ChooseClassroomForm, self).__init__(*args, **kwargs)
        self.fields['classroom']._choices = [(unicode(a), [(b.pk, unicode(b)) for b in a.classroom_set.all()]) for a in Building.objects.all()]
        self.fields['classroom'].queryset = Classroom.objects.all()
    
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
        super(LessonSearchForm, self).__init__(*args, **kwargs)
        self.fields['classroom']._choices = [(unicode(a), [(b.pk, unicode(b)) for b in a.classroom_set.all()]) for a in Building.objects.all()]
        self.fields['classroom'].queryset = Classroom.objects.all()