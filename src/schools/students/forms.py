from django import forms
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from schools.students.models import Student
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import HiddenInput

class CreateStudentForm(ModelForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text=_("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message=_("This value must contain only letters, numbers and underscores."))
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False, widget=HiddenInput)
    class Meta:
        exclude = ('user',)
        model = Student
        
    def save(self):
        student = super(CreateStudentForm, self).save(commit=False)
        user = User(username=self.cleaned_data['username'], first_name=student.first_name, last_name=student.last_name, email=student.email)
        user.set_password(student.first_name)
        user.save()
        student.user = user
        student.save()
        return student

class StudentForm(ModelForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text=_("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message=_("This value must contain only letters, numbers and underscores."))
#    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False, widget=HiddenInput)
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        if self.instance.user_id:
            self.fields['username'].initial=self.instance.user.username
    class Meta:
        exclude = ('user',)
        model = Student
        
    def save(self):
        student = super(StudentForm, self).save(commit=False)
        if student.user_id:
            student.user.first_name = student.first_name
            student.user.last_name = student.last_name
            student.user.email = student.email
            student.user.username = self.cleaned_data['username']
            student.user.save()
        student.save()
        return student
