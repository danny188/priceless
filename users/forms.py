from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput


class RegisterForm(UserCreationForm):
    """Form to register a new user"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Enter your email'}))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Set a password'}))
    first_name = forms.CharField(label="First Name (optional)", widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Enter your first name'}),required=False)
    last_name = forms.CharField(label="Last Name (optional)", widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Enter your last name'}), required=False)

    class Meta:
        model = User
        fields = ["email", 'first_name', 'last_name']


class UpdateUserSettingsForm(forms.ModelForm):
    """Form to update user settings"""
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))

    class Meta:
        model = User
        fields = ['email', 'receive_email_as_products_go_on_sale', 'receive_product_sale_summary_email', 'summary_email_day_of_week']



class CustomAuthForm(AuthenticationForm):
    """Login form"""
    username = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder':'Enter your password'}))

    class Meta:
        model = User
