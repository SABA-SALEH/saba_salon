from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view_cart'),
    path('add/<int:service_id>/', views.add_to_cart, name='add_to_cart'),
    path('add/package/<int:item_id>/', views.add_package_to_cart, name='add_package_to_cart'), 
    path('remove-from-cart/<str:item_type>/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('edit/<int:service_id>/', views.edit_cart_item, name='edit_cart_item'),
    path('<int:service_id>/get_available_times/', views.get_available_times, name='get_available_times'),
    path('<int:service_id>/get_booked_times/', views.get_booked_times, name='get_booked_times'),
]
   

