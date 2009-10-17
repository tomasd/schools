from django import forms
from schools.buildings.models import Building

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        
