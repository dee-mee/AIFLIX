from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users with email as the primary identifier."""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'

class CustomAuthenticationForm(AuthenticationForm):
    """Authentication form that accepts both email and username."""
    username = forms.CharField(label='Email / Username')
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Please enter a correct username/email and password. "
                    "Note that both fields may be case-sensitive."
                )
            
            self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data
