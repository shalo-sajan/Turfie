# bookings/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from turfs.models import Turf
from .models import Booking
from .forms import BookingForm, BookingStatusUpdateForm # Import the new form
from users.models import UserType # To check user type
from django.core.exceptions import ValidationError # Ensure ValidationError is imported

@login_required
def create_booking(request, turf_pk):
    """
    View for players to create a new booking for a specific turf.
    - Requires the user to be logged in and a 'Player'.
    - Retrieves the turf based on turf_pk.
    - Handles form display (GET) and submission (POST).
    """
    if not request.user.is_player():
        messages.error(request, "Only players can book turfs.")
        return redirect('turfs:turf_list') # Redirect to general turf list

    turf = get_object_or_404(Turf, pk=turf_pk, is_active=True)

    if request.method == 'POST':
        # Pass the turf instance to the form's constructor
        # This allows the model's clean method to access 'turf' during validation
        form = BookingForm(request.POST, instance=Booking(turf=turf))
        if form.is_valid():
            booking = form.save(commit=False) # Don't save to DB yet
            booking.player = request.user      # Assign the current player
            # booking.turf is already set via the instance passed to the form
            booking.status = Booking.BookingStatus.PENDING # Set initial status

            try:
                booking.save() # This will trigger the model's clean() method
                messages.success(request, f"Booking for {turf.name} on {booking.booking_date} from {booking.start_time} to {booking.end_time} is pending confirmation. Total: ₹{booking.total_price}")
                return redirect('bookings:booking_history') # Redirect to booking history
            except ValidationError as e:
                # Catch model-level validation errors (e.g., overlapping bookings)
                # Ensure message_dict is handled correctly
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
                else:
                    messages.error(request, f"Booking error: {e.message}") # Fallback for non-dict errors
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")

        else:
            # Display form errors to the user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = BookingForm() # Empty form for GET request

    context = {
        'form': form,
        'turf': turf,
        'form_title': f'Book Turf: {turf.name}'
    }
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_history(request):
    """
    Displays a list of bookings for the logged-in user.
    - Players see their own bookings.
    - Turf Owners see bookings for their turfs.
    - Admins see all bookings.
    """
    if request.user.is_player():
        bookings = Booking.objects.filter(player=request.user)
        context_heading = "My Booking History"
    elif request.user.is_turf_owner():
        # Get turfs owned by the current turf owner
        owned_turfs = request.user.owned_turfs.all()
        # Filter bookings for those turfs
        bookings = Booking.objects.filter(turf__in=owned_turfs)
        context_heading = "Bookings for My Turfs"
    elif request.user.is_admin():
        bookings = Booking.objects.all()
        context_heading = "All Bookings (Admin View)"
    else:
        bookings = Booking.objects.none()
        context_heading = "No Bookings Found"

    context = {
        'bookings': bookings,
        'heading': context_heading,
        'user_type': request.user.user_type, # Pass user type for conditional rendering
    }
    return render(request, 'bookings/booking_history.html', context)


@login_required
def manage_booking(request, pk):
    """
    Allows a Turf Owner or Admin to manage a specific booking's status.
    - Turf Owner can only manage bookings for their own turfs.
    - Admin can manage any booking.
    """
    booking = get_object_or_404(Booking, pk=pk)

    # Authorization check
    if request.user.is_turf_owner():
        # Ensure the booking's turf is owned by the current turf owner
        if booking.turf.owner != request.user:
            messages.error(request, "You are not authorized to manage this booking.")
            return redirect('bookings:booking_history') # Redirect to their booking history
    elif not request.user.is_admin():
        messages.error(request, "You are not authorized to manage bookings.")
        return redirect('bookings:booking_history') # Redirect if not owner or admin

    if request.method == 'POST':
        form = BookingStatusUpdateForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, f"Booking for {booking.turf.name} (ID: {booking.pk}) status updated to {booking.get_status_display()}.")
            return redirect('bookings:booking_history') # Redirect back to booking history
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = BookingStatusUpdateForm(instance=booking) # Pre-populate form with current status

    context = {
        'booking': booking,
        'form': form,
        'form_title': f'Manage Booking for {booking.turf.name}'
    }
    return render(request, 'bookings/manage_booking.html', context)

