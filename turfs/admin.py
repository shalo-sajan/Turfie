# turfs/admin.py

from django.contrib import admin
from .models import Turf

@admin.register(Turf)
class TurfAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Turf model.
    Customizes how Turf objects are displayed and managed in the Django admin.
    """
    list_display = ('name', 'owner', 'location', 'price_per_hour', 'is_active', 'created_at')
    list_filter = ('is_active', 'owner__user_type') # Filter by turf status and owner type
    search_fields = ('name', 'location', 'description', 'owner__username') # Search by turf name, location, description, owner username
    raw_id_fields = ('owner',) # Use a raw ID field for owner for better performance with many users
    date_hierarchy = 'created_at' # Add a date drill-down navigation
    ordering = ('-created_at',) # Default ordering

    # Customize the form for adding/editing a turf
    fieldsets = (
        (None, {
            'fields': ('name', 'owner', 'location', 'description', 'image')
        }),
        ('Pricing & Availability', {
            'fields': ('price_per_hour', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Make this section collapsible
        }),
    )
    readonly_fields = ('created_at', 'updated_at') # These fields are auto-managed

    # Pre-populate owner field for Turf Owners in admin (optional but useful)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser: # Only superusers can choose any owner
            # If the user is a turf owner, pre-fill the owner field with themselves
            # and make it read-only for them.
            if request.user.is_turf_owner():
                form.base_fields['owner'].initial = request.user
                form.base_fields['owner'].widget.attrs['disabled'] = 'disabled'
                form.base_fields['owner'].required = False # Not strictly needed if disabled, but good practice
        return form

    # Override save_model to handle disabled 'owner' field if needed
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and request.user.is_turf_owner():
            obj.owner = request.user # Ensure the owner is set to the current turf owner
        super().save_model(request, obj, form, change)

