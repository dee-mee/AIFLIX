from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm

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
    """Handle user login."""
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('movies:home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')
