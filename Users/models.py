# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

# A helper function to define the upload path for profile pictures
def user_profile_picture_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/profile_pics/user_<id>/<filename>
    return f'profile_pics/user_{instance.id}/{filename}'

class User(AbstractUser):
    """
    Custom User model to handle both Player and Turf Owner accounts.
    """
    USER_TYPE_CHOICES = (
        ('player', 'Player'),
        ('turf_owner', 'Turf Owner'),
    )

    # This is the new field for the profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        null=True, 
        blank=True, 
        default='profile_pics/default_avatar.png', # Provide a path to a default image
        verbose_name='Profile Picture'
    )

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='player',
        verbose_name='Account Type'
    )

    # Additional fields for Turf Owners
    business_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Business Name'
    )

    # Changed from phone_number to phone to match your HTML form
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Phone Number'
    )

    def __str__(self):
        return self.username

    @property
    def is_player(self):
        return self.user_type == 'player'

    @property
    def is_turf_owner(self):
        return self.user_type == 'turf_owner'
    
    def get_dashboard_url(self):
        """Returns the appropriate dashboard URL based on the user's type."""
        if self.is_turf_owner:
            return reverse('users:dashboard_turf_owner')
        else:
            return reverse('users:dashboard_player')