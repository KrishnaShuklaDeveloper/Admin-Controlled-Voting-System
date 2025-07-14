from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Candidate
from .models import Profile

# If this isn't already there
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# 👇 This is the form to update email and username (or more if you want)
class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    username = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'email']


# 👇 This handles profile image uploads
class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image']


# User Registration Form with Email
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address',
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Voting Form – allows choosing a candidate
class VoteForm(forms.Form):
    candidate = forms.ModelChoiceField(
        queryset=Candidate.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None
    )
