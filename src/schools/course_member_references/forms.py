from django import forms
from django.forms.widgets import Textarea
from schools.course_member_references.models import CourseMemberReference

class CourseMemberReferenceForm(forms.ModelForm):
    text = forms.CharField(widget=Textarea(attrs={"rows":2, 'style':'width: 90%;'}, ))
    class Meta:
        model = CourseMemberReference
