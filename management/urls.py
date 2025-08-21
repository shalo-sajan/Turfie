# management/urls.py
from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('turf-requests/', views.turf_requests_view, name='turf_requests'),
    path('turf-requests/<int:turf_id>/manage/', views.manage_turf_request_view, name='manage_turf_request'),
]
