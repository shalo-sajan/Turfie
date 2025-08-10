# Turfs/urls.py
from django.urls import path
from . import views

app_name = 'turfs' # This is important for namespacing

urlpatterns = [
    path('', views.turf_list_view, name='turf_list'),
    path('<int:turf_id>/', views.turf_detail_view, name='turf_detail'),
    # You would add URL patterns for booking here
]