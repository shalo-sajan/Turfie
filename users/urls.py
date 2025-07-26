# users/urls.py

from django.urls import path
from . import views

app_name = 'users' # Namespace for URLs, e.g., {% url 'users:login' %}

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('player-dashboard/', views.player_dashboard, name='player_dashboard'),
    path('turf-owner-dashboard/', views.turf_owner_dashboard, name='turf_owner_dashboard'),
]
