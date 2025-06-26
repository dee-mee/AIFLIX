from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm

def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please create a profile.')
            return redirect('profiles:profile_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    """Handle user login with Netflix-style interface."""
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next')
            if not next_url:
                return redirect('movies:home')
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    
    context = {
        'form': form,
        'next': request.GET.get('next', '')
    }
    return render(request, 'accounts/login_netflix.html', context)

@login_required
def profile(request):
    """Handle user profile and account settings."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        
        if 'update_profile' in request.POST and form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('accounts:profile')
            
        if 'change_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'password_form': password_form
    })

def user_logout(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('movies:home')
