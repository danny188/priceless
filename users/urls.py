from django.urls import path
from .views import RegisterView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    # path('change_password', auth_views.PasswordChangeView.as_view(template_name='registration/change_password.html', success_url='/'), name='change_password')
]