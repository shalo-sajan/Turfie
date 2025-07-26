# turfs/urls.py

from django.urls import path
from . import views

app_name = 'turfs' # Namespace for turf-related URLs

urlpatterns = [
    path('', views.turf_list, name='turf_list'), # List all turfs (or owned turfs)
    path('add/', views.turf_create, name='turf_create'), # Add new turf
    path('<int:pk>/edit/', views.turf_update, name='turf_update'), # Edit existing turf
    path('<int:pk>/delete/', views.turf_delete, name='turf_delete'), # Delete turf
    # Add a detail view later if needed: path('<int:pk>/', views.turf_detail, name='turf_detail'),
]
