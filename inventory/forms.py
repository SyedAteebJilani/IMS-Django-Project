from django import forms
from django.contrib.auth.models import User
from .models import Profile, Item, Purchase

class SignUpForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            if hasattr(user, 'profile'):
                user.profile.full_name = self.cleaned_data['full_name']
                user.profile.phone_number = self.cleaned_data['phone_number']
                user.profile.save()
        return user

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'company', 'selling_price', 'quantity', 'average_cost']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'e.g. Premium Notebook', 'autofocus': True}),
            'category': forms.Select(attrs={'class': 'form-select custom-input'}),
            'company': forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'Unknown'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control custom-input', 'placeholder': '0'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control custom-input', 'placeholder': '0'}),
            'average_cost': forms.NumberInput(attrs={'class': 'form-control custom-input', 'placeholder': '0'}),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['item', 'quantity', 'unit_price']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select custom-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control custom-input', 'placeholder': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control custom-input', 'placeholder': 'Cost per unit'}),
        }