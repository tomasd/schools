# -*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import HiddenInput, Textarea
from django.utils.translation import ugettext as _, ugettext
from schools.courses.models import CourseMember, Course
from schools.student_testing.models import TestingTerm, TestResult, StudentTest
from django.forms.util import ValidationError

class CreateTestingTermForm(forms.Form):
    student_test = forms.ModelChoiceField(queryset=StudentTest.objects.all(), required=False)
    name = forms.CharField(max_length=150, required=False)
    description = forms.CharField(required=False, widget=Textarea)
    max_score = forms.IntegerField(required=False)
    date = forms.DateField()
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=HiddenInput)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        if cleaned_data['student_test'] is None:
            if not cleaned_data['name'] or not cleaned_data['max_score']:
                raise forms.ValidationError(_(u'Musíte vybrať test, alebo zadať údaje pre vytvorenie nového testu.'))
        return cleaned_data

    def save(self):
        test = self.cleaned_data['student_test']
        if test is None:
            test = StudentTest(name=self.cleaned_data['name'], description=self.cleaned_data['description'], max_score=self.cleaned_data['max_score'], language=self.cleaned_data['course'].language)
            test.save()
        testing_term = TestingTerm(date=self.cleaned_data['date'], test=test, course=self.cleaned_data['course'])
        testing_term.save()
        return testing_term
         

        
class CreateTestResultForm(forms.ModelForm):
    course_member = forms.ModelChoiceField(queryset=CourseMember.objects.all(), widget=HiddenInput)
    description = forms.CharField(widget=Textarea(attrs={"rows":2, 'style':'width: 100%;'}, ))
    class Meta:
        model = TestResult
        exclude = ('testing_term', )
        

class TestingTermForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TestingTermForm, self).__init__(*args, **kwargs)
        self.fields['course'].widget = HiddenInput()
    class Meta:
        model = TestingTerm

class TestResultForm(forms.ModelForm):
    description = forms.CharField(widget=Textarea(attrs={"rows":2, 'style':'width: 100%;'}, ))
    class Meta:
        model = TestResult
        exclude = ('testing_term' )
        
    def limit_to_course(self, course):
        self.fields['course_member'].queryset = self.fields['course_member'].queryset.filter(course=course)
        

class EditTestResultForm(TestResultForm):
    def __init__(self, *args, **kwargs):
        super(EditTestResultForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance', False):
            self.fields['course_member'] = forms.ModelChoiceField(queryset=CourseMember.objects.all(), widget=HiddenInput)
            self.fields['course_member'].student = kwargs['instance'].course_member.student 
        
    def clean(self):
        terms_for_student = TestResult.objects.filter(
                  course_member=self.cleaned_data['course_member'], 
                  testing_term=self.cleaned_data['testing_term'])
        
        if self.cleaned_data['id']:
            terms_for_student = terms_for_student.exclude(pk=self.cleaned_data['id'].pk)
            
        if terms_for_student:
            raise ValidationError(ugettext(u'Študent môže písať naraz len jeden test, presvedčte sa že každý študent je vybraný práve raz.'))
        return self.cleaned_data