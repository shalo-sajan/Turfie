# users/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from Turfs.models import Booking, Turf

# Import your models from your apps
from .models import User
from Turfs.models import Turf, Booking # Assuming your models are in the 'Turfs' app

class register(View):
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # 1. Get all form data, including the file
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        account_type = request.POST.get('account_type', 'player')
        
        # The profile picture comes from request.FILES
        profile_picture = request.FILES.get('profile_picture')

        # --- Validation ---
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, self.template_name, request.POST)

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, self.template_name, request.POST)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, self.template_name, request.POST)

        try:
            # 2. Create the user with common fields first
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # 3. Add the optional and conditional fields
            user.user_type = account_type

            if profile_picture:
                user.profile_picture = profile_picture

            if account_type == 'turf_owner':
                user.business_name = request.POST.get('business-name')
                user.phone = request.POST.get('phone') 

            # 4. Save the user object with all the new data
            user.save()

            # --- Login and Redirect ---
            auth_login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Turfie.')
            
            if user.is_staff:  
                return redirect('management:admin_dashboard')
            elif user.is_turf_owner:
                return redirect('users:dashboard_turf_owner')
            else:
                return redirect('users:dashboard_player')

        except Exception as e:
            messages.error(request, f'An error occurred during registration: {e}')
            return render(request, self.template_name, request.POST)
        
        
def landing(request):
    return render(request, 'landing.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                if user.is_staff:  # Check if the user is an admin
                    return redirect('management:admin_dashboard')
                elif user.is_turf_owner:
                    return redirect('users:dashboard_turf_owner')
                else:
                    return redirect('users:dashboard_player')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please enter your username and password.")

    else: # GET request
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
def dashboard_turf_owner(request):
    current_owner = request.user

    # Get all turfs owned by the current user
    owner_turfs = Turf.objects.filter(owner=current_owner)

    # Calculate statistics using database aggregation for efficiency
    stats = Booking.objects.filter(turf__in=owner_turfs).aggregate(
        total_bookings=Count('id'),
        total_revenue=Sum('amount', default=0),
    )
    
    # Calculate average rating separately
    avg_rating = owner_turfs.aggregate(rating=Avg('rating', default=0))
    stats['avg_rating'] = avg_rating['rating']

    # Get the 5 most recent bookings for this owner's turfs
    recent_bookings = Booking.objects.filter(turf__in=owner_turfs).order_by('-start_time')[:5]

    # Package all the data into a context dictionary
    context = {
        'user': current_owner,
        'stats': stats,
        'recent_bookings': recent_bookings,
    }

    return render(request, 'dashboard_turf_owner.html', context)

@login_required
def dashboard_player(request):
    now = timezone.now()
    
    # Fetch the next 2 upcoming bookings for the dashboard preview
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        start_time__gte=now
    ).select_related('turf').order_by('start_time')[:2]
    
    

    # You can keep your logic for recommended turfs here
    recommended_turfs = Turf.objects.filter(approval_status='approved').order_by('-rating')[:3]
    
    
    context = {
        'user': request.user,
        'upcoming_bookings': upcoming_bookings,
        'recommended_turfs': recommended_turfs,
        'notification_count': 3 # Placeholder
    }
    return render(request, 'dashboard_player.html', context)

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')

# "my bookings view"
@login_required
def my_bookings_view(request):
    """
    Displays a list of the current user's past and upcoming bookings.
    """
    now = timezone.now()
    # Get bookings and prefetch the related turf to avoid extra database queries in the loop
    all_bookings = Booking.objects.filter(user=request.user).select_related('turf').order_by('-start_time')

    upcoming_bookings = all_bookings.filter(start_time__gte=now)
    past_bookings = all_bookings.filter(start_time__lt=now)

    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
    }
    return render(request, 'users/my_bookings.html', context)