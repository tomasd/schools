# -*- coding: utf-8 -*-
from django import forms
from django.forms.util import ValidationError
from django.utils.translation import ugettext as _
from schools.companies.models import Company

class InvoiceForm(forms.Form):
    start = forms.DateField()
    end = forms.DateField()
    companies = forms.ModelMultipleChoiceField(queryset=Company.objects.all(), required=False)
    show_students = forms.BooleanField(required=False)
    
    def clean(self):
        if 'start' in self.cleaned_data and 'end' in self.cleaned_data:
            if not self.cleaned_data['start'] <= self.cleaned_data['end']:
                raise ValidationError(_(u'Začiatok musí byť menší ako koniec'))
        return self.cleaned_data