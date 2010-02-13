from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
class CompanyUserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class CompanyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')