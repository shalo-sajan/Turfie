# Users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Renamed to avoid confusion
from .models import User # Import your custom User model

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin): # Use BaseUserAdmin here
    # Add 'user_type', 'business_name', 'phone_number' to fieldsets and list_display
    # to make them visible and editable in the admin.

    # 1. Fieldsets for editing existing users
    fieldsets = BaseUserAdmin.fieldsets + ( # Use BaseUserAdmin.fieldsets
        ('User Type & Specific Info', {'fields': ('user_type', 'business_name', 'phone_number')}),
    )

    # 2. Fieldsets for creating new users (this is often different and critical)
    # UserAdmin has `add_fieldsets` for the "Add user" page.
    add_fieldsets = BaseUserAdmin.add_fieldsets + ( # Use BaseUserAdmin.add_fieldsets
        ('User Type & Specific Info', {'fields': ('user_type', 'business_name', 'phone_number')}),
    )

    # The 'list_display' control which fields are shown in the user list view.
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active')
    
    # The 'search_fields' allow searching by these fields.
    search_fields = ('username', 'email', 'business_name')

    # Optional: If you want to filter users by user_type in the admin list
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')