# bookings/urls.py

from django.urls import path
from . import views # Import views from the current app

app_name = 'bookings' # Namespace for bookings-related URLs

urlpatterns = [
    # URL for creating a booking for a specific turf
    path('book/<int:turf_pk>/', views.create_booking, name='create_booking'),
    # URL for viewing booking history
    path('history/', views.booking_history, name='booking_history'),
    # URL for managing individual bookings (approve/reject/cancel)
    path('<int:pk>/manage/', views.manage_booking, name='manage_booking'),
]
