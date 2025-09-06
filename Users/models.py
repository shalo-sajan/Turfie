# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from Turfs.models import Turf

# A helper function to define the upload path for profile pictures
def user_profile_picture_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/profile_pics/user_<id>/<filename>
    return f'profile_pics/user_{instance.id}/{filename}'

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('player', 'Player'),
        ('turf_owner', 'Turf Owner'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='player')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    business_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    favorites = models.ManyToManyField(Turf, related_name='favorited_by', blank=True)
    bio = models.TextField(max_length=500, blank=True) # New bio field
    
    def __str__(self):
        return self.username

    @property
    def is_player(self):
        return self.user_type == 'player'

    @property
    def is_turf_owner(self):
        return self.user_type == 'turf_owner'
    
    def get_dashboard_url(self):
        if self.is_staff:
            return reverse('management:admin_dashboard')
        elif self.is_turf_owner:
            return reverse('users:dashboard_turf_owner')
        else:
            return reverse('users:dashboard_player')