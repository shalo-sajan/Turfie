# turfs/models.py

from django.db import models
from users.models import CustomUser # Import our custom user model

class Turf(models.Model):
    """
    Model representing a single turf (e.g., a football turf, cricket pitch).
    Each turf is owned by a CustomUser with the 'Turf Owner' role.
    """
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE, # If owner is deleted, their turfs are also deleted
        limit_choices_to={'user_type': 'TURF_OWNER'}, # Only Turf Owners can be assigned as owners
        related_name='owned_turfs', # Allows accessing turfs from a CustomUser instance (e.g., owner.owned_turfs.all())
        verbose_name="Turf Owner"
    )
    name = models.CharField(max_length=255, verbose_name="Turf Name")
    location = models.CharField(max_length=255, verbose_name="Location")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    price_per_hour = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Price per Hour (e.g., 1000.00)"
    )
    # This will store the path to the image file.
    # You'll need to configure MEDIA_ROOT and MEDIA_URL in settings.py later for actual image serving.
    image = models.ImageField(
        upload_to='turf_images/', # Images will be saved in MEDIA_ROOT/turf_images/
        blank=True,
        null=True,
        verbose_name="Turf Image"
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for the Turf model.
        Orders turfs by creation date by default.
        """
        verbose_name = "Turf"
        verbose_name_plural = "Turfs"
        ordering = ['-created_at'] # Order by most recently created first

    def __str__(self):
        """
        String representation of the Turf model.
        """
        return f"{self.name} ({self.location})"

    def get_absolute_url(self):
        """
        Returns the URL to access a particular turf instance.
        (Will be implemented later when we have detail views)
        """
        # from django.urls import reverse
        # return reverse('turfs:turf_detail', args=[str(self.id)])
        return "#" # Placeholder for now
