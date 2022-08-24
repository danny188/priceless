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
def update_user_settings_view(request):
    """Display or updates user settings"""
    if request.method == 'POST':
        form = UpdateUserSettingsForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your settings are updated successfully', extra_tags="is-success is-light")

    else:
        form = UpdateUserSettingsForm(instance=request.user)

    return render(request, 'users/settings.html', {'form': form})


@login_required
def delete_account_confirm_view(request):
    """Shows page to confirm account deletion"""
    return render(request, "users/delete_account_confirm.html")


@login_required
def delete_account_view(request):
    """Deletes a user account along with their product_set"""

    if request.method == "POST":
        confirm_account_email = request.POST.get("confirm-email").strip()

        if request.user.email == confirm_account_email:
            # delete linked products of user
            request.user.product_set.all().delete()
            # delete user
            request.user.delete()

            return redirect("/")
        else:
            messages.warning(request, 'The email address you entered did not match your account email', extra_tags="is-warning is-light")

            return render(request, "users/delete_account_confirm.html")

