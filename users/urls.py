from django.urls import path, re_path
from .views import RegisterView, update_user_settings
from django.contrib.auth import views as auth_views

from .forms import CustomAuthForm

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('settings', update_user_settings, name='settings'),
    re_path(r'^login/$', auth_views.LoginView.as_view(authentication_form=CustomAuthForm), name='login'),
]