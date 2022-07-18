from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input'}))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'input'}))
    first_name = forms.CharField(label="First Name (optional)", widget=forms.TextInput(attrs={'class': 'input'}),required=False)
    last_name = forms.CharField(label="Last Name (optional)", widget=forms.TextInput(attrs={'class': 'input'}), required=False)

    class Meta:
        model = User
        fields = ["email", 'first_name', 'last_name']


class UpdateUserSettingsForm(forms.ModelForm):
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))


    class Meta:
        model = User
        fields = ['email', 'email_alert_frequency', 'email_alert_day_of_week', 'pause_email_alerts']
