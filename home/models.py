from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()

class ContactMessage(models.Model):
    """Store contact form submissions"""

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
    """Gym Membership Model"""

    MEMBERSHIP_CHOICES = [
        ('rookie', 'Rookie — $39/mo'),
        ('warrior', 'Warrior — $79/mo'),
        ('elite', 'Elite — $129/mo'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gym_membership')
    membership_plan = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='rookie')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Membership details
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Payment info
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_membership_plan_display()}"

    class Meta:
        ordering = ['-created_at']


class WorkoutLog(models.Model):
    """Store user workout logs"""

    WORKOUT_TYPES = [
        ('strength', 'Strength'),
        ('hiit', 'HIIT'),
        ('cardio', 'Cardio'),
        ('combat', 'Combat Sports'),
        ('yoga', 'Yoga / Mobility'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPES)
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    duration_minutes = models.IntegerField()
    calories_burned = models.IntegerField()
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.workout_type} - {self.date}"


class WeightLog(models.Model):
    """Store user weight tracking"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weight_logs')
    weight = models.DecimalField(max_digits=5, decimal_places=1, help_text="Weight in lbs")
    date = models.DateField(default=timezone.now)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.weight} lbs - {self.date}"


class BodyMetrics(models.Model):
    """Store body composition metrics"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='body_metrics')
    body_fat = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Body fat percentage")
    muscle_mass = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="Muscle mass in lbs")
    bmi = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Body metrics"

    def __str__(self):
        return f"{self.user.username} - Body metrics - {self.date}"


class PersonalBest(models.Model):
    """Store user personal bests"""

    EXERCISE_CHOICES = [
        ('bench_press', 'Bench Press'),
        ('squat', 'Squat'),
        ('deadlift', 'Deadlift'),
        ('pull_ups', 'Pull-ups'),
        ('ohp', 'Overhead Press'),
        ('run_5k', '5K Run'),
        ('run_10k', '10K Run'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_bests')
    exercise = models.CharField(max_length=50, choices=EXERCISE_CHOICES)
    value = models.CharField(max_length=50, help_text="e.g., '225' or '24:12'")
    unit = models.CharField(max_length=20, default='lbs')
    date = models.DateField(default=timezone.now)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.get_exercise_display()}: {self.value} {self.unit}"


class PointsTransaction(models.Model):
    """Store user points/achievements"""

    TRANSACTION_TYPES = [
        ('workout', 'Workout Completed'),
        ('streak', 'Streak Bonus'),
        ('milestone', 'Milestone Achieved'),
        ('referral', 'Referral Bonus'),
        ('checkin', 'Daily Check-in'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points')
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.points} points"


class UserStreak(models.Model):
    """Track user workout streaks"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_workout_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Streak: {self.current_streak} days"


class UserSettings(models.Model):
    """Store user preferences and notification settings"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')

    # Notification settings
    workout_reminders = models.BooleanField(default=True)
    pt_alerts = models.BooleanField(default=True)
    weight_reminder = models.BooleanField(default=True)
    promo_emails = models.BooleanField(default=False)
    class_confirmations = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s settings"

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