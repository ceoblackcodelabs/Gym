from django import forms
from home.models import GymMembership


class GymMembershipForm(forms.ModelForm):
    class Meta:
        model = GymMembership
        fields = [
            'user',
            'membership_plan',
            'status',
            'end_date',
            'payment_method',
            'last_payment_date',
        ]

        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'membership_user'
            }),
            'membership_plan': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'membership_plan'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'membership_status'
            }),
            'end_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'id': 'membership_end_date'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'payment_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Visa ending in 1234',
                'id': 'membership_payment_method'
            }),
            'last_payment_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                    'id': 'membership_last_payment'
                },
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['end_date'].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields['last_payment_date'].input_formats = ('%Y-%m-%dT%H:%M',)

        # Make fields optional
        self.fields['end_date'].required = False
        self.fields['payment_method'].required = False
        self.fields['last_payment_date'].required = False

        # Add help texts
        self.fields['membership_plan'].help_text = "Select the membership tier"
        self.fields['status'].help_text = "Current membership status"
        self.fields['end_date'].help_text = "When does this membership expire? (Optional)"
        self.fields['payment_method'].help_text = "Credit card or payment method (Optional)"