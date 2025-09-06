from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Sum, Count, Avg
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_POST

from Turfs.models import Turf, Booking
from .models import User
from .forms import UserProfileForm
from .decorators import player_required, turf_owner_required
from datetime import date

# =============================================================================
# AUTHENTICATION & CORE VIEWS
# =============================================================================

class register(View):
    """Handles new user registration."""
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        account_type = request.POST.get('account_type', 'player')
        profile_picture = request.FILES.get('profile_picture')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, self.template_name, {'form_data': request.POST})
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, self.template_name, {'form_data': request.POST})
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, self.template_name, {'form_data': request.POST})

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.user_type = account_type
            if profile_picture:
                user.profile_picture = profile_picture
            if account_type == 'turf_owner':
                user.business_name = request.POST.get('business-name')
                user.phone = request.POST.get('phone') 
            user.save()

            auth_login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Turfie.')
            return redirect(user.get_dashboard_url())
        except Exception as e:
            messages.error(request, f'An error occurred during registration: {e}')
            return render(request, self.template_name, {'form_data': request.POST})

def landing(request):
    """Renders the public landing page."""
    return render(request, 'landing.html')

def login_view(request):
    """Handles user login and redirects based on user type."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect(user.get_dashboard_url())
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """Logs the user out and redirects to the landing page."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:landing')

# =============================================================================
# DASHBOARD VIEWS
# =============================================================================

@login_required
@turf_owner_required 
def dashboard_turf_owner(request):
    """Displays the dashboard for turf owners with key statistics."""
    owner_turfs = Turf.objects.filter(owner=request.user)
    stats = Booking.objects.filter(turf__in=owner_turfs).aggregate(
        total_bookings=Count('id'),
        total_revenue=Sum('amount', default=0),
    )
    avg_rating = owner_turfs.aggregate(rating=Avg('rating', default=0))
    stats['avg_rating'] = avg_rating['rating'] if avg_rating['rating'] else 0
    recent_bookings = Booking.objects.filter(turf__in=owner_turfs).order_by('-start_time')[:5]
    todays_bookings = Booking.objects.filter(turf__in=owner_turfs, start_time__date=date.today()).order_by('start_time')

    context = {
        'stats': stats,
        'recent_bookings': recent_bookings,
        'todays_bookings': todays_bookings,
    }
    return render(request, 'users/dashboard_turf_owner.html', context)


@login_required
@player_required
def dashboard_player(request):
    """Displays the dashboard for players with upcoming bookings and recommendations."""
    now = timezone.now()
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        start_time__gte=now
    ).select_related('turf').order_by('start_time')[:10]
    
    recommended_turfs = Turf.objects.filter(
        approval_status='approved', 
        owner__is_active=True
    ).order_by('-rating')[:10]
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'recommended_turfs': recommended_turfs,
        'notification_count': 3  # Placeholder
    }
    return render(request, 'users/dashboard_player.html', context)

# =============================================================================
# PLAYER-SPECIFIC PAGES
# =============================================================================

@login_required
@player_required
def my_bookings_view(request):
    """Displays a list of the user's past and upcoming bookings."""
    now = timezone.now()
    all_bookings = Booking.objects.filter(user=request.user).select_related('turf').order_by('-start_time')
    context = {
        'upcoming_bookings': all_bookings.filter(start_time__gte=now),
        'past_bookings': all_bookings.filter(start_time__lt=now),
    }
    return render(request, 'users/my_bookings.html', context)

@login_required
@player_required
def favorites_view(request):
    """Displays a list of the user's favorite turfs."""
    favorite_turfs = request.user.favorites.all()
    context = {'favorite_turfs': favorite_turfs}
    return render(request, 'users/favorites.html', context)

# =============================================================================
# PROFILE MANAGEMENT
# =============================================================================

@login_required
def edit_profile_view(request):
    """
    Handles both profile information updates and password changes from a single page.
    """
    active_tab = 'profile'
    
    if request.method == 'POST':
        # Initialize forms with POST data if available
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if 'update_profile' in request.POST:
            active_tab = 'profile'
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('users:edit_profile')
        
        elif 'change_password' in request.POST:
            active_tab = 'password'
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                # ✅ Add a special tag to the success message
                messages.success(request, 'Your password was successfully updated!', extra_tags='password-success')
                return redirect('users:edit_profile')
    else:
        # Initialize empty forms for GET request
        profile_form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    
    context = {
        'form': profile_form,
        'password_form': password_form,
        'active_tab': active_tab,
    }
    return render(request, 'users/edit_profile.html', context)

# ✅ ADDED THE MISSING CLASS-BASED VIEW
class UserPasswordChangeView(PasswordChangeView):
    """
    Uses Django's built-in view for securely handling password changes.
    This is now handled within edit_profile_view but is kept for URL resolution if needed.
    """
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('users:edit_profile')

    def form_valid(self, form):
        messages.success(self.request, 'Your password was successfully updated!')
        return super().form_valid(form)

@login_required
@require_POST
def delete_account_view(request):
    """Deletes the user's account permanently."""
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, 'Your account has been successfully deleted.')
    return redirect('users:landing')

# =============================================================================
# API-LIKE ENDPOINTS (for JavaScript calls)
# =============================================================================

@login_required
@require_POST
def toggle_favorite_view(request, turf_id):
    """Adds or removes a turf from the user's favorites list."""
    turf = get_object_or_404(Turf, id=turf_id)
    if turf in request.user.favorites.all():
        request.user.favorites.remove(turf)
        is_favorite = False
    else:
        request.user.favorites.add(turf)
        is_favorite = True
    return JsonResponse({'is_favorite': is_favorite})

