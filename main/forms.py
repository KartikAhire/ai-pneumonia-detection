from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Patient, XRay, Report, UserProfile

class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with Bootstrap styling"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class PatientForm(forms.ModelForm):
    """Form for creating and updating patients"""
    class Meta:
        model = Patient
        fields = ['name', 'date_of_birth', 'gender', 'guardian_name', 'phone', 'email', 'address', 'medical_history']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class XRayUploadForm(forms.ModelForm):
    """Form for uploading X-ray images"""
    class Meta:
        model = XRay
        fields = ['patient', 'image', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ReportForm(forms.ModelForm):
    """Form for creating medical reports"""
    class Meta:
        model = Report
        fields = ['diagnosis', 'recommendations', 'severity']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
        }


class UserProfileForm(forms.ModelForm):
    """Form for updating user profiles"""
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone', 'specialty', 'bio']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UserForm(forms.ModelForm):
    """Form for updating user information"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
