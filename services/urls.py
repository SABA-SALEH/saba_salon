from django.urls import path
from . import views

app_name = 'services'
urlpatterns = [
    path('', views.all_services, name='all_services'),
    path('<int:service_id>/', views.service_detail, name='service_detail'),
]
