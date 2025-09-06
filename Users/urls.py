# users/urls.py

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('player-dashboard/', views.dashboard_player, name='dashboard_player'),
    path('turf-owner-dashboard/', views.dashboard_turf_owner, name='dashboard_turf_owner'),


    
    # Player-specific pages
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('toggle-favorite/<int:turf_id>/', views.toggle_favorite_view, name='toggle_favorite'),

    # Profile Management
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('account/delete/', views.delete_account_view, name='delete_account'),
]


