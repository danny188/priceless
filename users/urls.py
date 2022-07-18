from django.urls import path
from .views import RegisterView, update_user_settings
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('settings', update_user_settings, name='update-settings'),
    # path('change_password', auth_views.PasswordChangeView.as_view(template_name='registration/change_password.html', success_url='/'), name='change_password')
]