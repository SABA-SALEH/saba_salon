from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('add/', views.add_staff_member, name='add_staff_member'),
    path('staff/<int:pk>/edit/', views.edit_staff_member, name='edit_staff_member'),
    path('staff/<int:pk>/delete/', views.delete_staff_member, name='delete_staff_member'),
]
