from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last name'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }))

    # Account type selection during registration
    account_type = forms.ChoiceField(
        choices=Profile.AccountType.choices,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial=Profile.AccountType.FAN
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Set account type when creating profile
            Profile.objects.filter(user=user).update(
                account_type=self.cleaned_data['account_type']
            )
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username or Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'account_type', 'bio', 'location', 'birth_date', 'avatar',
            'website', 'social_instagram', 'social_twitter', 'social_youtube',
            'favorite_genres'
        ]
        widgets = {
            'account_type': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your location'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'social_instagram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Instagram username'
            }),
            'social_twitter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Twitter username'
            }),
            'social_youtube': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'YouTube channel URL'
            }),
            'favorite_genres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Rock, Pop, Jazz, Electronic'
            }),
        }