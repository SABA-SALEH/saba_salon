from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.all_services, name='all_services'),
    path('<int:service_id>/', views.service_detail, name='service_detail'),
    path('<int:service_id>/get_available_times/', views.get_available_times, name='get_available_times'),
    path('<int:service_id>/get_booked_times/', views.get_booked_times, name='get_booked_times'),
]
