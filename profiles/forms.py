from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    """Form for creating and updating user profiles."""
    class Meta:
        model = Profile
        fields = ['name', 'avatar', 'is_kids', 'maturity_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'maturity_level': forms.Select(attrs={'class': 'form-select'}),
            'is_kids': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['maturity_level'].required = False
        self.fields['avatar'].required = False

class ProfileSelectionForm(forms.Form):
    """Form for selecting a profile."""
    profile = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect(attrs={'class': 'profile-radio'}),
        empty_label=None
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['profile'].queryset = user.profiles.all()
