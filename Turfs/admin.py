# Turfs/admin.py
from django.contrib import admin
from .models import Turf, Booking

@admin.register(Turf)
class TurfAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'owner', 'price_per_hour', 'rating')
    search_fields = ('name', 'location')
    list_filter = ('owner',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('turf', 'user', 'start_time', 'status', 'amount')
    search_fields = ('turf__name', 'user__username')
    list_filter = ('status', 'turf')