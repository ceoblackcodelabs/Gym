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

# testimonials
class Testimonial(models.Model):
    """Store gym member testimonials"""

    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]

    # Author information
    name = models.CharField(max_length=200, help_text="Full name of the testimonial author")
    initials = models.CharField(max_length=5, blank=True, help_text="Auto-generated from name")

    # Testimonial content
    content = models.TextField(help_text="The testimonial message")
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)

    # Member info
    member_since = models.CharField(max_length=100, blank=True, help_text="e.g., 'Member for 2 years'")
    membership_plan = models.CharField(max_length=50, blank=True, help_text="e.g., 'Warrior Plan'")

    # Optional link to actual user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='testimonials'
    )

    # Display settings
    is_active = models.BooleanField(default=True, help_text="Show this testimonial on the website")
    is_featured = models.BooleanField(default=False, help_text="Feature this testimonial prominently")
    display_order = models.IntegerField(default=0, help_text="Lower numbers appear first")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.name} - {self.rating}★"

    def save(self, *args, **kwargs):
        # Auto-generate initials from name
        if not self.initials and self.name:
            name_parts = self.name.split()
            if len(name_parts) >= 2:
                self.initials = (name_parts[0][0] + name_parts[1][0]).upper()
            else:
                self.initials = self.name[:2].upper()
        super().save(*args, **kwargs)

    def get_star_display(self):
        """Return HTML star rating"""
        return '★' * self.rating + '☆' * (5 - self.rating)

    def get_avatar_color(self):
        """Generate consistent color based on name"""
        colors = ["#44ff33", "#70ff6b", "#6cff47", "#73ff50", "#48ff48"]
        hash_val = sum(ord(c) for c in self.name) % len(colors)
        return colors[hash_val]