from django import forms
from schools.courses.models import Course, CourseMember, ExpenseGroup, Lesson,\
    LessonAttendee
from django.forms.widgets import HiddenInput

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        
class CourseMemberForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    class Meta:
        model = CourseMember
        
    def limit_to_course(self, course):
        self.fields['expense_group'].queryset = self.fields['expense_group'].queryset.filter(course=course) 
        
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
        fields = ('realized', 'real_classroom', 'real_lector', 'real_lector_price', 'real_start', 'real_end', 'real_content', 'course')

class LessonAttendeeForm(forms.ModelForm):
    class Meta:
        model = LessonAttendee
        
    def limit_to_course(self, course):
        self.fields['course_member'].queryset = self.fields['course_member'].queryset.filter(course=course)