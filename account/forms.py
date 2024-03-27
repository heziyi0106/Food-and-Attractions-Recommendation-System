from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
# from django.utils.translation import ugettext_lazy as _

from account.models import *


class RegistrationForm(forms.Form):

    account = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    username = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],widget=forms.RadioSelect)
    birthday = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d'))
    email = forms.EmailField()
    phone = forms.CharField(max_length=10)





