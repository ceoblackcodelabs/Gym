from django.db import models
from django.utils import timezone
from users.models import User

# Create your models here.
class Expense(models.Model):
    name = models.CharField(max_length=50, default="expense")
    description = models.TextField(default="")
    date = models.DateTimeField(default=timezone.now)
    price = models.IntegerField(default=0)

class Income(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=255, blank=True, null=True)
    date_received = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_received']

    def __str__(self):
        return f"{self.title} - {self.amount}"

# check in
from home.models import GymMembership
class DailyCheckIn(models.Model):
    """Track gym member attendance / daily check-ins"""

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('missed', 'Missed'),
    ]

    # Link to active gym member
    member = models.ForeignKey(
        GymMembership,
        on_delete=models.CASCADE,
        related_name='checkins'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')

    checkin_time = models.DateTimeField(default=timezone.now)
    checkin_date = models.DateField(default=timezone.now)

    notes = models.TextField(blank=True, null=True)

    # Optional: staff who recorded attendance
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_checkins'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-checkin_date', '-checkin_time']
        unique_together = ['member', 'checkin_date']  # prevents double check-in per day

    def __str__(self):
        return f"{self.member.user.username} - {self.status} - {self.checkin_date}"