from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import ContactMessage, GymMembership

User = get_user_model()

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['first_name', 'last_name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'John'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'john@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+1 (555) 000-0000'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Tell us how we can help...', 'rows': 4}),
        }


class MembershipRegistrationForm(forms.Form):
    """Form for registering a new member (creates User + Profile + GymMembership)"""
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'John'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Doe'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'john@example.com'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+1 (555) 000-0000'})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    membership_plan = forms.ChoiceField(
        choices=GymMembership.MEMBERSHIP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fitness_goal = forms.ChoiceField(
        choices=GymMembership.GOAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Create a password'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm password'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists. Please login instead.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 10:
            raise forms.ValidationError('Please enter a valid phone number with at least 10 digits.')
        return phone

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except forms.ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data

    def save(self, commit=True):
        """Create User, Profile, and GymMembership"""
        data = self.cleaned_data

        # Create username from email (or generate)
        username = data['email'].split('@')[0]
        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create User
        user = User.objects.create_user(
            username=username,
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        # Update Profile with additional info
        if hasattr(user, 'profile'):
            profile = user.profile
            # Add phone to profile if the field exists
            if hasattr(profile, 'phone'):
                profile.phone = data['phone']
            profile.birth_date = data['date_of_birth']
            profile.save()

        # Create Gym Membership
        membership = GymMembership.objects.create(
            user=user,
            membership_plan=data['membership_plan'],
            fitness_goal=data['fitness_goal'],
            status='active'
        )

        return user, membership