# users/urls.py

from django.urls import path
from . import views

app_name = 'users' # Namespace for URLs, e.g., {% url 'users:login' %}

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register.as_view(), name='register'),
    path('turf-owner-dashboard/', views.dashboard_turf_owner, name='dashboard_turf_owner'),
    path('player-dashboard/', views.dashboard_player, name='dashboard_player'),
    path('logout/', views.logout_view, name='logout'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
        path('favorites/', views.favorites_view, name='favorites'),
    path('toggle-favorite/<int:turf_id>/', views.toggle_favorite_view, name='toggle_favorite'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
]
