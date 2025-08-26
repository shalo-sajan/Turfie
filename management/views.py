# management/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count,Q
from django.db.models.functions import TruncMonth
from Users.models import User
from Turfs.models import Turf, Booking
import calendar
from datetime import datetime, date, timedelta
import json
from django.utils import timezone

@staff_member_required
def admin_dashboard_view(request):
    # --- Top Stat Cards (no change) ---
    total_users = User.objects.count()
    total_turfs = Turf.objects.count()
    total_bookings = Booking.objects.filter(status='confirmed').count()
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0

    # --- Booking Calendar Logic ---
    today = timezone.now()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    selected_date = date(year, month, 1)
    prev_month = selected_date - timedelta(days=1)
    next_month = (selected_date + timedelta(days=32)).replace(day=1)

    cal = calendar.Calendar()
    month_days = cal.monthdatescalendar(year, month)
    
    bookings_in_month = Booking.objects.filter(
        start_time__year=year,
        start_time__month=month,
        status='confirmed'
    ).values('start_time__day').annotate(count=Count('id'))
    
    booking_counts = {b['start_time__day']: b['count'] for b in bookings_in_month}

    # --- 3-Month Trend Analytics ---
    three_months_ago = today.replace(day=1) - timedelta(days=60)
    
    user_trends = (
        User.objects.filter(date_joined__gte=three_months_ago)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    revenue_trends = (
        Booking.objects.filter(start_time__gte=three_months_ago, status='confirmed')
        .annotate(month=TruncMonth('start_time'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    user_chart_labels = [d['month'].strftime('%b %Y') for d in user_trends]
    user_chart_data = [d['count'] for d in user_trends]
    revenue_chart_labels = [d['month'].strftime('%b %Y') for d in revenue_trends]
    revenue_chart_data = [float(d['total']) for d in revenue_trends]

    # --- Top Performers ---
    top_turf = Booking.objects.filter(status='confirmed').values('turf__name').annotate(count=Count('id')).order_by('-count').first()
    top_user = Booking.objects.filter(status='confirmed').values('user__username').annotate(count=Count('id')).order_by('-count').first()

    context = {
        'total_users': total_users,
        'total_turfs': total_turfs,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'month_days': month_days,
        'booking_counts': booking_counts,
        'current_month_str': selected_date.strftime('%B %Y'),
        'prev_month': prev_month,
        'next_month': next_month,
        'today': today.date(),
        'user_chart_labels': json.dumps(user_chart_labels),
        'user_chart_data': json.dumps(user_chart_data),
        'revenue_chart_labels': json.dumps(revenue_chart_labels),
        'revenue_chart_data': json.dumps(revenue_chart_data),
        'top_turf': top_turf,
        'top_user': top_user,
    }
    return render(request, 'management/admin_dashboard.html', context)

@staff_member_required
def turf_requests_view(request):
    """Displays a list of all turfs pending approval."""
    pending_turfs = Turf.objects.filter(approval_status='pending').order_by('created_at')
    
    context = {
        'pending_turfs': pending_turfs,
    }
    return render(request, 'management/turf_requests.html', context)


@require_POST # Ensures this view only accepts POST requests
@staff_member_required
def manage_turf_request_view(request, turf_id):
    """Handles the approval or rejection of a turf."""
    turf = get_object_or_404(Turf, id=turf_id)
    action = request.POST.get('action')

    if action == 'approve':
        turf.approval_status = 'approved'
        messages.success(request, f"'{turf.name}' has been approved and is now live.")
    elif action == 'reject':
        turf.approval_status = 'rejected'
        messages.warning(request, f"'{turf.name}' has been rejected.")
    
    turf.save()
    return redirect('management:turf_requests')


@staff_member_required
def manage_users_view(request):
    """Lists all users for the admin to manage."""
    # Exclude the current admin from the list to prevent self-blocking
    users = User.objects.filter(is_staff=False).order_by('username')
    context = {
        'users': users,
    }
    return render(request, 'management/manage_users.html', context)


@require_POST
@staff_member_required
def toggle_user_status_view(request, user_id):
    """Blocks or unblocks a user by toggling their 'is_active' status."""
    user_to_toggle = get_object_or_404(User, id=user_id)
    
    # Toggle the is_active status
    user_to_toggle.is_active = not user_to_toggle.is_active
    user_to_toggle.save()
    
    status = "unblocked" if user_to_toggle.is_active else "blocked"
    messages.success(request, f"User '{user_to_toggle.username}' has been {status}.")
    
    return redirect('management:manage_users')


@staff_member_required
def manage_turfs_view(request):
    """Lists all turfs with search and filter functionality for the admin."""
    turfs = Turf.objects.select_related('owner').order_by('-created_at')
    
    # --- Search and Filter Logic ---
    search_query = request.GET.get('q')
    status_filter = request.GET.get('status')

    if search_query:
        turfs = turfs.filter(
            Q(name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(owner__username__icontains=search_query)
        )
    
    if status_filter:
        turfs = turfs.filter(approval_status=status_filter)

    context = {
        'turfs': turfs,
        'search_query': search_query or "",
        'status_filter': status_filter or "",
    }
    return render(request, 'management/manage_turfs.html', context)

def manage_bookings_view(request):
    """Lists all bookings with search and filter functionality for the admin."""
    bookings = Booking.objects.select_related('turf', 'user').order_by('-start_time')
    
    # --- Search and Filter Logic ---
    search_query = request.GET.get('q')
    status_filter = request.GET.get('status')

    if search_query:
        bookings = bookings.filter(
            Q(turf__name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(id__icontains=search_query.replace('#BK-', ''))
        )
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    context = {
        'bookings': bookings,
        'search_query': search_query or "",
        'status_filter': status_filter or "",
    }
    return render(request, 'management/manage_bookings.html', context)

@staff_member_required
def booking_detail_admin_view(request, booking_id):
    """Displays the details of a single booking for the admin."""
    booking = get_object_or_404(Booking, id=booking_id)
    context = {
        'booking': booking,
    }
    return render(request, 'management/booking_detail_admin.html', context)
