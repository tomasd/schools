from django import forms
from schools.buildings.models import Building

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        
class ClassroomLessonsForm(forms.Form):
    start = forms.DateTimeField(required=False)
    end = forms.DateTimeField(required=False)