from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    path('', views.package_list, name='package_list'),
    path('add/', views.add_package, name='add_package'),
    path('edit/<int:package_id>/', views.edit_package, name='edit_package'),
    path('delete/<int:package_id>/', views.delete_package, name='delete_package'),
]
