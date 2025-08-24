# Turfs/forms.py

from django import forms
from .models import Turf, Amenity, Booking
from django.core.exceptions import ValidationError
from datetime import date,datetime, timedelta

class TurfForm(forms.ModelForm):
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Turf
        fields = [
            'name', 'description', 'main_image', 'price_per_hour',
            'address_line_1', 'city', 'district', 'state', 'pincode', 
            'google_maps_link', 'opening_time', 'closing_time', 'amenities'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'google_maps_link': forms.URLInput(attrs={'class': 'form-control'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control-file'}),
            # Add widgets for the new time fields
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

# --- NEW BOOKING FORM ---
class BookingForm(forms.Form):
    """ A form for players to book a time slot. """
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))

    def __init__(self, *args, **kwargs):
        # We need the turf to perform validation, so we pass it in when creating the form
        self.turf = kwargs.pop('turf', None)
        super().__init__(*args, **kwargs)
        
    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        if selected_date:
            if selected_date < date.today():
                raise ValidationError("You cannot book a date in the past.")
            if selected_date > (date.today() + timedelta(days=7)):
                raise ValidationError("You can only book up to 7 days in advance.")
        return selected_date
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if not all([date, start_time, end_time]):
            # If any field is missing, validation fails early
            return cleaned_data

        # Combine date and time for comparison
        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)

        # 1. Check for minimum 1-hour duration
        if (end_datetime - start_datetime) < timedelta(hours=1):
            raise ValidationError("Booking must be for at least 1 hour.")
        
        # 2. Check if booking is in the future
        if start_datetime < datetime.now():
            raise ValidationError("You cannot book a time in the past.")

        # 3. Check if end time is after start time
        if end_time <= start_time:
            raise ValidationError("End time must be after the start time.")

        # 4. Check if the booking falls within the turf's operating hours
        if not (self.turf.opening_time <= start_time and end_time <= self.turf.closing_time):
            raise ValidationError(f"Booking must be between {self.turf.opening_time.strftime('%I:%M %p')} and {self.turf.closing_time.strftime('%I:%M %p')}.")

        # 5. Check for overlapping bookings
        conflicting_bookings = Booking.objects.filter(
            turf=self.turf,
            start_time__lt=end_datetime,
            end_time__gt=start_datetime
        ).exclude(status='cancelled')

        if conflicting_bookings.exists():
            raise ValidationError("This time slot is already booked. Please choose another time.")

        return cleaned_data
