from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm

def register(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('movies:browse')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to AIFLIX.')
            return redirect('movies:home')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'registration/register.html', {
        'form': form,
        'next': request.GET.get('next', 'movies:home')
    })

def user_login(request):
    """Handle user login with Netflix-style interface."""
    if request.user.is_authenticated:
        return redirect('movies:browse')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                next_url = request.POST.get('next', 'movies:browse')
                return redirect(next_url)
            else:
                # This should not happen if form is valid, but just in case
                messages.error(request, 'Authentication failed. Please try again.')
        else:
            # Log form errors for debugging
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
            
            # If form is invalid, show appropriate error message
            if '__all__' in form.errors:
                for error in form.errors['__all__']:
                    if 'inactive' in error.lower():
                        messages.error(request, 'This account is inactive.')
                    else:
                        messages.error(request, 'Invalid email or password. Please try again.')
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomAuthenticationForm()
    
    context = {
        'form': form,
        'next': request.GET.get('next', 'movies:home')
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
    return redirect('landing')
