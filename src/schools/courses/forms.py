from django import forms
from schools.courses.models import Course, CourseMember, ExpenseGroup
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
