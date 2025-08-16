# Turfs/models.py

from django.db import models
from django.conf import settings

class Amenity(models.Model):
    """Represents a single amenity that a turf can offer, like Parking or Floodlights."""
    name = models.CharField(max_length=100, unique=True)
    # You can store the Font Awesome class, e.g., 'fas fa-parking'
    icon_class = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Amenities" # Corrects plural form in admin

    def __str__(self):
        return self.name

class Turf(models.Model):
    """Represents a single turf/venue that can be booked."""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='turfs_owned'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    main_image = models.ImageField(upload_to='turf_images/', blank=True, null=True)

    # --- New Detailed Location Fields ---
    address_line_1 = models.CharField(max_length=255, help_text="Street address, building, etc.")
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    google_maps_link = models.URLField(blank=True, null=True)
    
    # --- New Time Fields ---
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    # --- New Many-to-Many relationship for Amenities ---
    amenities = models.ManyToManyField(Amenity, blank=True)

    # --- Existing Fields ---
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # We are removing the old 'location' field. Migrations will handle this.

    def __str__(self):
        return f"{self.name} ({self.city})"

class Booking(models.Model):
    """Represents a booking made by a player for a specific turf."""
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
        related_name='bookings_made'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default='unpaid')
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.turf.name} by {self.user.username} on {self.start_time.strftime('%Y-%m-%d')}"

    @property
    def duration_hours(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600
        return 0
