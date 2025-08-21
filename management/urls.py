# management/urls.py
from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('turf-requests/', views.turf_requests_view, name='turf_requests'),
    path('turf-requests/<int:turf_id>/manage/', views.manage_turf_request_view, name='manage_turf_request'),
    path('manage-users/', views.manage_users_view, name='manage_users'),
    path('manage-users/<int:user_id>/toggle-status/', views.toggle_user_status_view, name='toggle_user_status'),
]
