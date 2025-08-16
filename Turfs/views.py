# Turfs/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Turf, Booking
from .forms import TurfForm, BookingForm
from datetime import datetime, date, time, timedelta

# --- Turf Management Views (No changes here) ---
@login_required
def turf_list_view(request):
    owner_turfs = Turf.objects.filter(owner=request.user)
    context = {'turfs': owner_turfs}
    return render(request, 'turfs/turf_list.html', context)

@login_required
def turf_add_view(request):
    if request.method == 'POST':
        form = TurfForm(request.POST, request.FILES)
        if form.is_valid():
            turf = form.save(commit=False)
            turf.owner = request.user
            turf.save()
            form.save_m2m() 
            messages.success(request, f"Successfully added '{turf.name}'.")
            return redirect('turfs:turf_list')
    else:
        form = TurfForm()
    context = {'form': form}
    return render(request, 'turfs/turf_add.html', context)

@login_required
def turf_edit_view(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    if turf.owner != request.user:
        messages.error(request, "You are not authorized to edit this turf.")
        return redirect('turfs:turf_list')
    if request.method == 'POST':
        form = TurfForm(request.POST, request.FILES, instance=turf)
        if form.is_valid():
            form.save()
            messages.success(request, f"Successfully updated '{turf.name}'.")
            return redirect('turfs:turf_list')
    else:
        form = TurfForm(instance=turf)
    context = {'form': form, 'turf': turf}
    return render(request, 'turfs/edit_turf.html', context)

@login_required
def turf_delete_view(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    if turf.owner != request.user:
        messages.error(request, "You are not authorized to delete this turf.")
        return redirect('turfs:turf_list')
    if request.method == 'POST':
        turf_name = turf.name
        turf.delete()
        messages.success(request, f"Successfully deleted '{turf_name}'.")
        return redirect('turfs:turf_list')
    context = {'turf': turf}
    return render(request, 'turfs/turf_confirm_delete.html', context)


# --- Turf Booking Views (Updated Logic) ---

@login_required
def turf_detail_view(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    
    # --- Time Slot Generation Logic ---
    # Get the date from the request's GET parameters, default to today
    selected_date_str = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

    # Get all bookings for this turf on the selected date
    bookings_on_date = Booking.objects.filter(
        turf=turf, 
        start_time__date=selected_date
    ).exclude(status='cancelled')

    # Generate all possible 1-hour slots for the day
    time_slots = []
    current_time = datetime.combine(selected_date, turf.opening_time)
    end_time = datetime.combine(selected_date, turf.closing_time)
    
    while current_time < end_time:
        slot_end_time = current_time + timedelta(hours=1)
        is_booked = any(b.start_time < slot_end_time and b.end_time > current_time for b in bookings_on_date)
        
        time_slots.append({
            'start_time': current_time.time(),
            'is_booked': is_booked
        })
        current_time += timedelta(hours=1)

    # --- Booking Form Handling ---
    if request.method == 'POST':
        booking_form = BookingForm(request.POST, turf=turf)
        if booking_form.is_valid():
            date_val = booking_form.cleaned_data['date']
            start_time_val = booking_form.cleaned_data['start_time']
            end_time_val = booking_form.cleaned_data['end_time']
            
            start_datetime = datetime.combine(date_val, start_time_val)
            end_datetime = datetime.combine(date_val, end_time_val)
            
            duration = (end_datetime - start_datetime).total_seconds() / 3600
            amount = duration * float(turf.price_per_hour)

            Booking.objects.create(
                turf=turf, user=request.user, start_time=start_datetime,
                end_time=end_datetime, amount=amount, status='pending'
            )
            
            messages.success(request, f"Your booking for {turf.name} is pending confirmation.")
            return redirect('users:dashboard_player')
    else:
        booking_form = BookingForm(turf=turf, initial={'date': selected_date})

    context = {
        'turf': turf,
        'booking_form': booking_form,
        'time_slots': time_slots,
        'selected_date': selected_date,
    }
    return render(request, 'turfs/turf_detail.html', context)
@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security check: ensure the user is either the player or the turf owner
    if request.user != booking.user and request.user != booking.turf.owner:
        messages.error(request, "You are not authorized to view this booking.")
        return redirect(request.user.get_dashboard_url())

    context = {'booking': booking}
    return render(request, 'turfs/booking_detail.html', context)