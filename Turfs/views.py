# Turfs/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Turf, Booking
from .forms import TurfForm, BookingForm
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Q
import qrcode
import io
import base64

# --- NEW BOOKING MANAGEMENT VIEW ---
try:
    from weasyprint import HTML
except OSError:
    HTML = None

@require_POST # This decorator ensures this view only accepts POST requests
@login_required
def manage_booking_view(request, booking_id):
    """
    Handles actions on a booking like confirm, reject, or cancel.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    action = request.POST.get('action')

    # Security check and action handling
    if action == 'confirm' and request.user == booking.turf.owner:
        booking.status = 'confirmed'
        messages.success(request, f"Booking #{booking.id} has been confirmed.")
    elif action == 'reject' and request.user == booking.turf.owner:
        booking.status = 'cancelled' # Or you could add a 'rejected' status
        messages.warning(request, f"Booking #{booking.id} has been rejected.")
    elif action == 'cancel' and request.user == booking.user:
        booking.status = 'cancelled'
        messages.info(request, "Your booking has been cancelled.")
    else:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect(request.user.get_dashboard_url())

    booking.save()
    return redirect('turfs:booking_detail', booking_id=booking.id)


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
    
    # --- Time Slot & Date Logic ---
    today = timezone.now().date()
    selected_date_str = request.GET.get('date', today.strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    max_date = today + timedelta(days=7)

    bookings_on_date = Booking.objects.filter(
        turf=turf, 
        start_time__date=selected_date
    ).exclude(status='cancelled')

    time_slots = []
    start_datetime_naive = datetime.combine(selected_date, turf.opening_time)
    end_datetime_naive = datetime.combine(selected_date, turf.closing_time)
    current_time = timezone.make_aware(start_datetime_naive)
    end_time = timezone.make_aware(end_datetime_naive)
    
    while current_time < end_time:
        slot_end_time = current_time + timedelta(hours=1)
        is_booked = any(b.start_time < slot_end_time and b.end_time > current_time for b in bookings_on_date)
        
        time_slots.append({
            'start_time': current_time.time(),
            'end_time': slot_end_time.time(), # Add end time for display
            'is_booked': is_booked
        })
        current_time += timedelta(hours=1)

    # --- Booking Form Handling ---
    if request.method == 'POST':
        booking_form = BookingForm(request.POST, turf=turf)
        if booking_form.is_valid():
            # ... (your existing POST logic remains the same)
            date_val = booking_form.cleaned_data['date']
            start_time_val = booking_form.cleaned_data['start_time']
            end_time_val = booking_form.cleaned_data['end_time']
            
            start_datetime = timezone.make_aware(datetime.combine(date_val, start_time_val))
            end_datetime = timezone.make_aware(datetime.combine(date_val, end_time_val))
            
            duration = (end_datetime - start_datetime).total_seconds() / 3600
            amount = duration * float(turf.price_per_hour)

            Booking.objects.create(
                turf=turf, user=request.user, start_time=start_datetime,
                end_time=end_datetime, amount=amount, status='pending'
            )
            
            messages.success(request, f"Your booking for {turf.name} is pending confirmation.")
            return redirect('users:my_bookings')
    else:
        booking_form = BookingForm(turf=turf, initial={'date': selected_date})

    context = {
        'turf': turf,
        'booking_form': booking_form,
        'time_slots': time_slots,
        'selected_date': selected_date,
        'today': today,
        'max_date': max_date,
    }
    return render(request, 'turfs/turf_detail.html', context)



@require_POST # This decorator ensures this view only accepts POST requests
@login_required
def manage_booking_view(request, booking_id):
    """
    Handles actions on a booking like confirm, reject, or cancel.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    action = request.POST.get('action')

    # Security check and action handling
    if action == 'confirm' and request.user == booking.turf.owner:
        booking.status = 'confirmed'
        messages.success(request, f"Booking #{booking.id} has been confirmed.")
    elif action == 'reject' and request.user == booking.turf.owner:
        booking.status = 'cancelled' # Or you could add a 'rejected' status
        messages.warning(request, f"Booking #{booking.id} has been rejected.")
    elif action == 'cancel' and request.user == booking.user:
        booking.status = 'cancelled'
        messages.info(request, "Your booking has been cancelled.")
    else:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect(request.user.get_dashboard_url())

    booking.save()
    return redirect('turfs:booking_detail', booking_id=booking.id)

from .models import Booking 

# ... (add this function with your other views)
@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security check: ensure the user is either the player or the turf owner
    if request.user != booking.user and request.user != booking.turf.owner:
        messages.error(request, "You are not authorized to view this booking.")
        return redirect(request.user.get_dashboard_url())

    context = {'booking': booking}
    # You will need to create this template next
    return render(request, 'turfs/booking_details.html', context)

@login_required
def booking_receipt_pdf_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user != booking.user and request.user != booking.turf.owner:
        messages.error(request, "You are not authorized to view this receipt.")
        return redirect(request.user.get_dashboard_url())

    # --- QR Code Generation (no change here) ---
    qr_data = (
        f"Booking ID: {booking.id}\n"
        f"Turf: {booking.turf.name}\n"
        f"Player: {booking.user.username}\n"
        f"Date: {booking.start_time.strftime('%d %b %Y')}"
    )
    qr_img = qrcode.make(qr_data)
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()

    # --- ✅ NEW: Image to Base64 Conversion ---
    turf_image_base64 = None
    if booking.turf.main_image:
        try:
            with booking.turf.main_image.open('rb') as image_file:
                turf_image_base64 = base64.b64encode(image_file.read()).decode()
        except FileNotFoundError:
            # Handle case where image file is missing
            turf_image_base64 = None

    context = {
        'booking': booking,
        'qr_image_base64': qr_image_base64,
        'turf_image_base64': turf_image_base64, # Pass the new variable to the template
    }
    html_string = render_to_string('turfs/receipt.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_BK-{booking.id}.pdf"'
    return response


@login_required
def turf_search_view(request):
    turfs = Turf.objects.filter(approval_status='approved', owner__is_active=True)
    query = request.GET.get('q')
    sort_by = request.GET.get('sort')

    if query:
        turfs = turfs.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(district__icontains=query)
        )

    if sort_by == 'price_asc':
        turfs = turfs.order_by('price_per_hour')
    elif sort_by == 'price_desc':
        turfs = turfs.order_by('-price_per_hour')
    elif sort_by == 'rating':
        turfs = turfs.order_by('-rating')

    context = {
        'turfs': turfs,
        'query': query or "",
        'sort_by': sort_by or "",
    }
    return render(request, 'turfs/turf_search.html', context)
