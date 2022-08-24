from django.urls import path, re_path
from .views import RegisterView, delete_account_confirm_view, delete_account_view, update_user_settings_view
from django.contrib.auth import views as auth_views

from .forms import CustomAuthForm

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('delete_account_confirm', delete_account_confirm_view, name='delete-account-confirm'),
    path('delete_account', delete_account_view, name='delete-account'),
    path('settings', update_user_settings_view, name='settings'),
    re_path(r'^login/$', auth_views.LoginView.as_view(authentication_form=CustomAuthForm), name='login'),
]