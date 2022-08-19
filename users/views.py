# views.py
from django.shortcuts import render, redirect
from .forms import RegisterForm, UpdateUserSettingsForm
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib import messages

class RegisterView(generic.CreateView):
    form_class = RegisterForm
    success_url = "/products"
    template_name = "users/register.html"



@login_required
def update_user_settings(request):
    if request.method == 'POST':
        form = UpdateUserSettingsForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your settings are updated successfully', extra_tags="is-success is-light")

    else:
        form = UpdateUserSettingsForm(instance=request.user)

    return render(request, 'users/settings.html', {'form': form})