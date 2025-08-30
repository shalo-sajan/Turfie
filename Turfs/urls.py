# Turfs/urls.py
from django.urls import path
from . import views

app_name = 'turfs' # This is important for namespacing

urlpatterns = [
    path('', views.turf_list_view, name='turf_list'),
    path('<int:turf_id>/', views.turf_detail_view, name='turf_detail'),
    path('add/', views.turf_add_view, name='turf_add'),
    path('<int:turf_id>/edit/', views.turf_edit_view, name='turf_edit'),
    path('<int:turf_id>/delete/', views.turf_delete_view, name='turf_delete'),
    path('bookings/<int:booking_id>/', views.booking_detail_view, name='booking_detail'),
    path('bookings/<int:booking_id>/manage/', views.manage_booking_view, name='manage_booking'),
    path('bookings/<int:booking_id>/receipt/', views.booking_receipt_pdf_view, name='booking_receipt'),
        # --- Player-Facing Views ---
    path('search/', views.turf_search_view, name='turf_search'),
    path('<int:turf_id>/', views.turf_detail_view, name='turf_detail'),
]