# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages # For displaying success/error messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def register(request):
    """
    View for user registration.
    Handles both GET (displaying the empty form) and POST (processing form submission).
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log the user in immediately after registration
            messages.success(request, "Registration successful. Welcome!")
            # Redirect based on user type after successful registration
            if user.is_turf_owner():
                return redirect('users:turf_owner_dashboard') # To be created later
            else: # Default to player dashboard
                return redirect('users:player_dashboard') # To be created later
        else:
            # Display form errors to the user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    """
    View for user login.
    Handles both GET (displaying the empty form) and POST (processing form submission).
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                # Redirect based on user type after successful login
                if user.is_admin():
                    return redirect('admin:index') # Redirect to Django admin for admins
                elif user.is_turf_owner():
                    return redirect('users:turf_owner_dashboard') # To be created later
                else: # Default to player dashboard
                    return redirect('users:player_dashboard') # To be created later
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required # Ensures only logged-in users can access this view
def user_logout(request):
    """
    View for user logout.
    Logs out the current user and redirects to the login page.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('users:login')

# Placeholder dashboards (will be expanded later)
@login_required
def player_dashboard(request):
    return render(request, 'users/player_dashboard.html', {'user': request.user})

@login_required
def turf_owner_dashboard(request):
    return render(request, 'users/turf_owner_dashboard.html', {'user': request.user})

