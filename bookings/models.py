# bookings/models.py

from django.db import models
from users.models import CustomUser # Import our custom user model
from turfs.models import Turf       # Import the Turf model
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime
import decimal # Import the decimal module

class Booking(models.Model):
    """
    Model representing a single booking of a turf.
    """
    # Choices for booking status
    class BookingStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        COMPLETED = 'COMPLETED', 'Completed'

    player = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'PLAYER'}, # Only players can make bookings
        related_name='player_bookings',
        verbose_name="Booked By"
    )
    turf = models.ForeignKey(
        Turf,
        on_delete=models.CASCADE,
        related_name='turf_bookings',
        verbose_name="Turf Booked"
    )
    booking_date = models.DateField(verbose_name="Booking Date")
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Price",
        # Make total_price nullable for a brief moment before calculation
        # It will be populated by the save method, so it won't be null in DB
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name="Booking Status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for the Booking model.
        - Orders bookings by booking date and start time.
        - Adds a unique constraint to prevent overlapping bookings for the same turf.
        """
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['booking_date', 'start_time']
        # Ensure no overlapping bookings for the same turf at the same time
        # This constraint needs careful handling with time slots,
        # but is a good initial step.
        # For more robust time slot management, a separate Slot model might be better.
        unique_together = ('turf', 'booking_date', 'start_time', 'end_time')


    def __str__(self):
        """
        String representation of the Booking model.
        """
        return f"Booking for {self.turf.name} by {self.player.username} on {self.booking_date} from {self.start_time} to {self.end_time}"

    def clean(self):
        """
        Custom validation for the booking model.
        Ensures end_time is after start_time and prevents past bookings.
        """
        super().clean()

        if self.start_time and self.end_time:
            # Combine with a dummy date to create datetime objects for comparison
            dummy_date = datetime.date(2000, 1, 1)
            start_dt_for_comparison = datetime.datetime.combine(dummy_date, self.start_time)
            end_dt_for_comparison = datetime.datetime.combine(dummy_date, self.end_time)
            if start_dt_for_comparison >= end_dt_for_comparison:
                raise ValidationError("End time must be after start time.")

        if self.booking_date:
            # Prevent booking in the past
            if self.booking_date < timezone.now().date():
                raise ValidationError("Booking date cannot be in the past.")
            # If booking for today, ensure start_time is not in the past
            if self.booking_date == timezone.now().date() and self.start_time:
                # Compare time objects directly
                if self.start_time < timezone.now().time():
                    raise ValidationError("Start time cannot be in the past for today's booking.")

        # Check for overlapping bookings (more robust check than unique_together for time ranges)
        # This check is crucial for preventing double bookings.
        # It checks if any existing booking for the same turf on the same date
        # overlaps with the proposed new booking time range.
        if self.turf and self.booking_date and self.start_time and self.end_time:
            # Exclude the current booking itself if it's an update
            query = Booking.objects.filter(
                turf=self.turf,
                booking_date=self.booking_date,
                # Check for overlaps:
                # (StartA < EndB) AND (EndA > StartB)
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                # Corrected: Refer to BookingStatus using self.BookingStatus
                status__in=[self.BookingStatus.PENDING, self.BookingStatus.CONFIRMED] # Only consider active bookings
            )
            if self.pk: # If updating an existing booking, exclude itself from the overlap check
                query = query.exclude(pk=self.pk)

            if query.exists():
                raise ValidationError("This time slot is already booked for this turf.")

    def save(self, *args, **kwargs):
        """
        Override save method to calculate total_price before saving.
        """
        # Calculate total price based on duration and turf's price_per_hour
        # This calculation MUST happen BEFORE full_clean()
        if self.start_time and self.end_time and self.turf and self.turf.price_per_hour is not None:
            start_dt = datetime.datetime.combine(self.booking_date, self.start_time)
            end_dt = datetime.datetime.combine(self.booking_date, self.end_time)
            duration = (end_dt - start_dt).total_seconds() / 3600 # Duration in hours
            # Corrected: Convert duration (float) to Decimal before multiplication
            # Then, quantize the result to 2 decimal places
            self.total_price = (self.turf.price_per_hour * decimal.Decimal(str(duration))).quantize(
                decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP
            )
        else:
            self.total_price = decimal.Decimal('0.00') # Default to Decimal '0.00'

        # Now call full_clean() after total_price has been set
        self.full_clean() # This will call self.clean() and validate_unique()

        super().save(*args, **kwargs)

