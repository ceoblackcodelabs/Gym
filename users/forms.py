from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from home.models import GymMembership
from .models import Profile
from home.models import WeightLog, WorkoutLog, BodyMetrics

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

class WorkoutLogForm(forms.ModelForm):
    """Form for logging workouts"""

    class Meta:
        model = WorkoutLog
        fields = ['workout_type', 'title', 'notes', 'duration_minutes', 'calories_burned', 'date']
        widgets = {
            'workout_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Deadlift Day'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'How did it go?', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '60'}),
            'calories_burned': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '450'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class WeightLogForm(forms.ModelForm):
    """Form for logging weight"""

    class Meta:
        model = WeightLog
        fields = ['weight', 'date', 'notes']
        widgets = {
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '185.5', 'step': '0.5'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'notes': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional notes'}),
        }


class BodyMetricsForm(forms.ModelForm):
    """Form for logging body metrics"""

    class Meta:
        model = BodyMetrics
        fields = ['body_fat', 'muscle_mass', 'bmi', 'date']
        widgets = {
            'body_fat': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '18.5', 'step': '0.1'}),
            'muscle_mass': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '155', 'step': '0.1'}),
            'bmi': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '24.5', 'step': '0.1'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@example.com'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+1 (555) 000-0000'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id if self.instance else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email


class ProfileExtendedForm(forms.ModelForm):
    """Form for updating profile extended info"""

    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'goal_weight', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Tell us about yourself', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City, State'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'goal_weight': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '175', 'step': '1'}),
            'avatar': forms.FileInput(attrs={'class': 'form-input'}),
        }


class UserSettingsForm(forms.ModelForm):
    """Form for user notification settings"""

    class Meta:
        model = User
        fields = []  # We'll use the UserSettings model
        exclude = []


class MembershipUpgradeForm(forms.Form):
    """Form for upgrading membership plan"""

    membership_plan = forms.ChoiceField(
        choices=GymMembership.MEMBERSHIP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('visa', 'Visa'),
            ('mastercard', 'Mastercard'),
            ('amex', 'American Express'),
            ('paypal', 'PayPal'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    card_number = forms.CharField(
        max_length=16,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '**** **** **** 1234'})
    )
    expiry_date = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'MM/YY'})
    )
    cvv = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '123'})
    )

    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        # Remove spaces and check length
        card_number = card_number.replace(' ', '')
        if len(card_number) < 15 or len(card_number) > 16:
            raise forms.ValidationError('Please enter a valid card number.')
        return card_number


class DateRangeForm(forms.Form):
    """Form for filtering data by date range"""

    date_range = forms.ChoiceField(
        choices=[
            ('1m', 'Last Month'),
            ('3m', 'Last 3 Months'),
            ('6m', 'Last 6 Months'),
            ('1y', 'Last Year'),
            ('all', 'All Time'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )

class ProfileForm(forms.ModelForm):
    """Form for updating user profile - Simplified (No Creator/Fan)"""

    class Meta:
        model = Profile
        fields = [
            'bio', 'location', 'birth_date', 'avatar', 'goal_weight'
        ]
        widgets = {
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
            'goal_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Goal weight (lbs)',
                'step': '1'
            }),
        }


class UserUpdateForm(forms.ModelForm):
    """Form for updating base user info"""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email