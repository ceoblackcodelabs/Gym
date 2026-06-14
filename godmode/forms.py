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
            'end_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'last_payment_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['end_date'].input_formats = (
            '%Y-%m-%dT%H:%M',
        )

        self.fields['last_payment_date'].input_formats = (
            '%Y-%m-%dT%H:%M',
        )