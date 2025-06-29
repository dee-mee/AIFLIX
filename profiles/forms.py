from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    """Form for creating and updating user profiles with kids' profile support."""
    KIDS_AVATAR_CHOICES = [
        ('avatar1.png', '🦊 Fox'),
        ('avatar2.png', '🐱 Cat'),
        ('avatar3.png', '🐼 Panda'),
        ('avatar4.png', '🐘 Elephant'),
        ('avatar5.png', '🦁 Lion'),
    ]
    
    kids_avatar = forms.ChoiceField(
        choices=KIDS_AVATAR_CHOICES,
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Kids Avatar"
    )
    
    class Meta:
        model = Profile
        fields = ['name', 'avatar', 'is_kids', 'maturity_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'profile-name'}),
            'maturity_level': forms.Select(attrs={'class': 'form-select', 'id': 'maturity-level'}),
            'is_kids': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'is-kids'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['maturity_level'].required = False
        self.fields['avatar'].required = False
        
        # Set initial kids avatar if this is a kids profile
        if self.instance and self.instance.is_kids and self.instance.avatar:
            self.fields['kids_avatar'].initial = self.instance.avatar.name.split('/')[-1]
    
    def clean(self):
        cleaned_data = super().clean()
        is_kids = cleaned_data.get('is_kids')
        maturity_level = cleaned_data.get('maturity_level')
        kids_avatar = cleaned_data.get('kids_avatar')
        
        # If this is a kids profile
        if is_kids:
            # Set maturity level to appropriate for kids if not set or too high
            if not maturity_level or maturity_level not in ['all', '7+']:
                cleaned_data['maturity_level'] = '7+'
            
            # Set the kids avatar
            if kids_avatar:
                cleaned_data['avatar'] = f'avatars/kids/{kids_avatar}'
        
        return cleaned_data

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
