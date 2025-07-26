# bookings/admin.py

from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Booking model.
    Customizes how Booking objects are displayed and managed in the Django admin.
    """
    list_display = ('turf', 'player', 'booking_date', 'start_time', 'end_time', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'booking_date', 'turf', 'player')
    search_fields = ('turf__name', 'player__username') # Search by turf name or player username
    raw_id_fields = ('player', 'turf') # Use raw ID fields for better performance with many users/turfs
    date_hierarchy = 'booking_date'
    ordering = ('-booking_date', '-start_time',) # Order by most recent bookings first

    fieldsets = (
        (None, {
            'fields': ('turf', 'player', 'booking_date', 'start_time', 'end_time')
        }),
        ('Booking Details', {
            'fields': ('total_price', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('total_price', 'created_at', 'updated_at') # Total price is calculated, others are auto-managed

    # Override save_model to ensure clean() method is called for validation
    def save_model(self, request, obj, form, change):
        # Call the full_clean method to run model's clean() method (including custom validation)
        # This is important for custom validation like overlapping bookings
        obj.full_clean()
        super().save_model(request, obj, form, change)

