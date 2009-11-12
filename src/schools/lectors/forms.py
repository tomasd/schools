from django import forms
from schools.lectors.models import Contract, Lector
from django.forms.widgets import HiddenInput

class ContractForm(forms.ModelForm):
    lector = forms.ModelChoiceField(queryset=Lector.objects.all(), widget=HiddenInput)
    class Meta:
        model = Contract
