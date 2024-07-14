from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout, name='checkout'),  
    path('success/<str:order_number>/<str:email>/', views.checkout_success, name='checkout_success'),
    path('wh/', webhook, name='webhook'),
]
