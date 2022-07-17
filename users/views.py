# views.py
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.views import generic

class RegisterView(generic.CreateView):
    form_class = RegisterForm
    success_url = "/"
    template_name = "register.html"