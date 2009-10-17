from django import forms
from schools.courses.models import Course, CourseMember, ExpenseGroup, Lesson
from django.forms.widgets import HiddenInput

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        
class CourseMemberForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    class Meta:
        model = CourseMember
        
class ExpenseGroupForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    class Meta:
        model = ExpenseGroup        

class LessonPlanForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    class Meta:
        model = Lesson
        fields = ('course', 'classroom', 'start', 'end',)
        
class LessonRealizedForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    class Meta:
        model = Lesson
        fields = ('realized', 'real_classroom', 'real_lector', 'real_lector_price', 'real_start', 'real_end', 'real_content')
