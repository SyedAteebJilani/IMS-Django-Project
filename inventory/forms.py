from django import forms
from django.contrib.auth.models import User
from .models import Profile, Item, Purchase, Category

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

class UserProfileForm(forms.ModelForm):
    # Fields from User Model
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control custom-input'}))
    
    # Fields from Profile Model
    full_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control custom-input'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control custom-input'}))
    business_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'e.g. My Stationery Shop'}))

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['full_name'].initial = self.user.profile.full_name
            self.fields['phone_number'].initial = self.user.profile.phone_number
            self.fields['business_name'].initial = self.user.profile.business_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            if hasattr(user, 'profile'):
                user.profile.full_name = self.cleaned_data['full_name']
                user.profile.phone_number = self.cleaned_data['phone_number']
                user.profile.business_name = self.cleaned_data['business_name']
                user.profile.save()
        return user

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'company', 'selling_price', 'quantity', 'average_cost']
        labels = {
            'average_cost': 'Buying Price (Cost)',
        }
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

    def __init__(self, user=None, *args, **kwargs):
        super(PurchaseForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['item'].queryset = Item.objects.filter(user=user)

    # REMOVED: clean() method that was blocking price changes.
    # Now, the Purchase.save() method in models.py will handle the averaging math.

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'e.g. Office Supplies', 'autofocus': True}),
        }