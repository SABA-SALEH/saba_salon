from django.urls import path
from . import views
from .webhooks import webhook

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout, name='checkout'),  
    path('success/<str:order_number>/<str:email>/', views.checkout_success, name='checkout_success'),
    path('cache_checkout_data/', views.cache_checkout_data, name='cache_checkout_data'),
    path('wh/', webhook, name='webhook'),
]