# Turfs/admin.py
from django.contrib import admin
from .models import Turf, Booking, Amenity # Make sure to import Amenity

@admin.register(Turf)
class TurfAdmin(admin.ModelAdmin):
    # Replace 'location' with 'city' and 'district'
    list_display = ('name', 'city', 'district', 'owner', 'price_per_hour', 'rating')
    search_fields = ('name', 'city', 'district') # Update search fields as well
    list_filter = ('owner', 'city', 'state')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('turf', 'user', 'start_time', 'status', 'amount')
    search_fields = ('turf__name', 'user__username')
    list_filter = ('status', 'turf')

# Also register your new Amenity model so you can add amenities in the admin
@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')
    search_fields = ('name',)