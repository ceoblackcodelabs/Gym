from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('membership', 'Membership Info'),
        ('training', 'Personal Training'),
        ('corporate', 'Corporate Membership'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-created_at']


class GymMembership(models.Model):
    MEMBERSHIP_CHOICES = [
        ('rookie', 'Rookie — $39/mo'),
        ('warrior', 'Warrior — $79/mo'),
        ('elite', 'Elite — $129/mo'),
    ]

    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_building', 'Muscle Building'),
        ('endurance', 'Endurance & Cardio'),
        ('general', 'General Fitness'),
        ('athletic', 'Athletic Performance'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    # Use AUTH_USER_MODEL or get_user_model() for the relationship
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # This uses your custom User model
        on_delete=models.CASCADE,
        related_name='gym_membership'
    )
    membership_plan = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='rookie')
    fitness_goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='general')

    # Membership details
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Payment info (simplified)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_membership_plan_display()}"

    class Meta:
        ordering = ['-created_at']