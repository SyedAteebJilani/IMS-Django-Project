from django import forms
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def save(self, commit=True):
        # 1. Create User instance but don't save to DB yet
        user = super().save(commit=False)
        # 2. Set the password correctly (hashes it)
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            # 3. Update the Profile (created automatically by signal in models.py)
            if hasattr(user, 'profile'):
                user.profile.full_name = self.cleaned_data['full_name']
                user.profile.phone_number = self.cleaned_data['phone_number']
                user.profile.save()
                
        return user