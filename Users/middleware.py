# Users/middleware.py

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

class CheckUserActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # This code runs on every request
        
        # Check if the user is authenticated and if their account is now inactive
        if request.user.is_authenticated and not request.user.is_active:
            # Log the user out
            logout(request)
            
            # Add a message for the user
            messages.warning(request, "Your account has been deactivated. Please contact support.")
            
            # Redirect to the login page
            return redirect('users:login') # Or your landing page

        # If the user is active or not logged in, continue as normal
        response = self.get_response(request)
        return response
