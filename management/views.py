# management/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from Users.models import User
from Turfs.models import Turf, Booking
import json

@staff_member_required # Ensures only staff/admins can access this page
def admin_dashboard_view(request):
    # Calculate key statistics
    total_users = User.objects.count()
    total_turfs = Turf.objects.count()
    total_bookings = Booking.objects.filter(status='confirmed').count()
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0

    # Data for "Bookings per Month" chart
    bookings_per_month = (
        Booking.objects
        .annotate(month=TruncMonth('start_time'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Format data for Chart.js
    chart_labels = [b['month'].strftime('%b %Y') for b in bookings_per_month]
    chart_data = [b['count'] for b in bookings_per_month]

    context = {
        'total_users': total_users,
        'total_turfs': total_turfs,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
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
    users = User.objects.exclude(id=request.user.id).order_by('username')
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


