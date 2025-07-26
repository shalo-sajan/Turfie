# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Import UserAdmin
from .models import CustomUser

# Register your CustomUser model with the admin site.
# You can use the default UserAdmin for basic functionality,
# or create a custom admin class if you need to customize
# how CustomUser appears and is managed in the admin.

# Option 1: Simple registration (if you don't need custom admin fields yet)
admin.site.register(CustomUser)

# Option 2: More advanced registration (recommended for custom user models)
# This allows you to customize the fields shown in the admin for CustomUser
# class CustomUserAdmin(UserAdmin):
#     # Add 'user_type' to the fields displayed in the admin list view
#     list_display = UserAdmin.list_display + ('user_type',)
#
#     # Add 'user_type' to the fields shown when adding/changing a user
#     fieldsets = UserAdmin.fieldsets + (
#         (('User Type'), {'fields': ('user_type',)}),
#     )
#
#     # Register the CustomUser model with your custom admin class
#     admin.site.register(CustomUser, CustomUserAdmin)

