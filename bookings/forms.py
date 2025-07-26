# bookings/forms.py

from django import forms
from .models import Booking
import datetime

class BookingForm(forms.ModelForm):
    """
    Form for players to create a new booking.
    It allows selection of booking date, start time, and end time.
    The 'turf' and 'player' fields will be set by the view.
    """
    # Custom fields for date and time to allow specific widgets or validation
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Select Date"
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Start Time"
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="End Time"
    )

    class Meta:
        model = Booking
        # Only expose fields that the player will directly input
        fields = ['booking_date', 'start_time', 'end_time']

    def clean(self):
        """
        Custom form-level validation.
        This will run after individual field validations.
        """
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if booking_date and start_time and end_time:
            # Basic validation: end time must be after start time
            # Combine with a dummy date for comparison
            dummy_date = datetime.date(2000, 1, 1)
            start_dt_for_comparison = datetime.datetime.combine(dummy_date, start_time)
            end_dt_for_comparison = datetime.datetime.combine(dummy_date, end_time)

            if start_dt_for_comparison >= end_dt_for_comparison:
                self.add_error('end_time', "End time must be after start time.")

            # Prevent booking in the past
            if booking_date < datetime.date.today():
                self.add_error('booking_date', "Booking date cannot be in the past.")
            elif booking_date == datetime.date.today():
                if start_time < datetime.datetime.now().time():
                    self.add_error('start_time', "Start time cannot be in the past for today's booking.")

        return cleaned_data


class BookingStatusUpdateForm(forms.ModelForm):
    """
    Form for Turf Owners to update the status of a booking.
    """
    class Meta:
        model = Booking
        fields = ['status']
        labels = {
            'status': 'Change Status To'
        }
        # Only allow specific status changes by turf owners
        widgets = {
            'status': forms.Select(choices=[
                (Booking.BookingStatus.PENDING, 'Pending'),
                (Booking.BookingStatus.CONFIRMED, 'Confirmed'),
                (Booking.BookingStatus.CANCELLED, 'Cancelled'),
            ])
        }

    def clean_status(self):
        """
        Custom validation for status changes.
        Prevents changing status from CANCELLED or COMPLETED.
        """
        new_status = self.cleaned_data['status']
        current_status = self.instance.status

        if current_status in [Booking.BookingStatus.CANCELLED, Booking.BookingStatus.COMPLETED]:
            raise forms.ValidationError("Cannot change status of a cancelled or completed booking.")

        # Add more complex status transition logic here if needed, e.g.:
        # if current_status == Booking.BookingStatus.PENDING and new_status == Booking.BookingStatus.COMPLETED:
        #     raise forms.ValidationError("Cannot directly mark pending booking as completed.")

        return new_status

