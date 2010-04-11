# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.forms.util import ValidationError
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext_lazy as _, ugettext
from schools.companies.models import Company
from schools.students.models import Student
from django.core import mail

class CreateStudentForm(ModelForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text=_("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message=_("This value must contain only letters, numbers and underscores."))
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False, widget=HiddenInput)
    self_payer = forms.BooleanField(label=_(u'Samoplatca'), required=False)
    company = forms.ModelChoiceField(queryset=Company.objects.only_firmy(), required=False)
    class Meta:
        exclude = ('user',)
        model = Student
        
    def clean(self):
        if not self.cleaned_data['self_payer'] and self.cleaned_data['company'] is None:
            raise ValidationError(ugettext(u'Špecifikovali ste študenta samoplatcu, zaškrtnite políčko samoplatca.'))
        return self.cleaned_data
        
    def save(self):
        student = super(CreateStudentForm, self).save(commit=False)
        if self.cleaned_data['company'] is None:
            copy_fields = ['street', 'postal', 'town', 'phone', 'mobile', 'fax', 'www', 'email']
            company = Company(name=unicode(student), self_payer=True,
                               **dict([(a, getattr(student, a)) for a in copy_fields]))
            company.save()
            student.company = company
        user = User(username=self.cleaned_data['username'], first_name=student.first_name, last_name=student.last_name, email=student.email)
        password = User.objects.make_random_password(6)
        user.set_password(password)
        user.save()
        student.user = user
        student.save()
        if user.email:
            message = u'''
                Váš účet bol vytvorený. 
                Prihlasovacie meno: %s
                Heslo: %s
            ''' % (user.username, password)
            mail.send_mail(ugettext(u'Účet vytvorený'), message, None, [user.email], fail_silently=False)
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
