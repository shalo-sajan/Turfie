

from django.contrib.auth.models import AbstractUser
from django.db import models

# Define choices for user types
# This makes it easy to manage and ensures consistency
class UserType(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    TURF_OWNER = 'TURF_OWNER', 'Turf Owner'
    PLAYER = 'PLAYER', 'Player'

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    This model adds a 'user_type' field to differentiate between
    Admin, Turf Owner, and Player roles.
    """
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.PLAYER, # Default to 'Player' for new registrations
        verbose_name="User Type"
    )

    # Add related_name to avoid clashes with default User model's groups and user_permissions
    # This is necessary because CustomUser will be the AUTH_USER_MODEL
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.',
        related_name="customuser_set", # Custom related_name
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set", # Custom related_name
        related_query_name="customuser",
    )

    def __str__(self):
        """
        String representation of the CustomUser.
        Returns the username and their user type.
        """
        return f"{self.username} ({self.get_user_type_display()})"

    # You can add more methods here if needed, e.g., to check user type
    def is_admin(self):
        return self.user_type == UserType.ADMIN

    def is_turf_owner(self):
        return self.user_type == UserType.TURF_OWNER

    def is_player(self):
        return self.user_type == UserType.PLAYER

