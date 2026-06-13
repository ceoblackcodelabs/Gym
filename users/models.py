from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    # Add custom fields if needed
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username

class Profile(models.Model):

    class AccountType(models.TextChoices):
        CREATOR = 'creator', 'Creator'
        FAN = 'fan', 'Fan'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    account_type = models.CharField(
        max_length=10,
        choices=AccountType.choices,
        default=AccountType.FAN,
        help_text="Select account type: Creator or Fan"
    )
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: Additional fields for Creators
    website = models.URLField(blank=True, null=True, help_text="Creator's website or portfolio")
    social_instagram = models.CharField(max_length=100, blank=True, null=True)
    social_twitter = models.CharField(max_length=100, blank=True, null=True)
    social_youtube = models.CharField(max_length=100, blank=True, null=True)

    # Optional: Additional fields for Fans
    favorite_genres = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated list of favorite genres")

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.get_account_type_display()})"

    @property
    def is_creator(self):
        return self.account_type == self.AccountType.CREATOR

    @property
    def is_fan(self):
        return self.account_type == self.AccountType.FAN

# Signal to automatically create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()