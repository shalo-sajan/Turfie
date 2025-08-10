# Turfs/models.py

from django.db import models
from django.conf import settings # Best practice for linking to the User model

# Create your models here.

class Turf(models.Model):
    """
    Represents a single turf/venue that can be booked.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='turfs_owned',
        help_text="The user who owns and manages this turf."
    )
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, help_text="e.g., 'Koramangala, Bengaluru'")
    description = models.TextField(blank=True)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    
    # For the main image of the turf. Pillow library is required: pip install Pillow
    main_image = models.ImageField(upload_to='turf_images/', blank=True, null=True)
    
    # Rating can be calculated based on reviews later
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.location})"


class Booking(models.Model):
    """
    Represents a booking made by a player for a specific turf.
    """
    # Define status choices for the booking
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bookings_made',
        help_text="The player who made the booking."
    )
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # You can add payment details here later
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default='unpaid')

    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.turf.name} by {self.user.username} on {self.start_time.strftime('%Y-%m-%d')}"

    @property
    def duration_hours(self):
        """Calculates the duration of the booking in hours."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600
        return 0

