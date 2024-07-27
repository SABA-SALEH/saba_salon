from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<str:entity_type>/<int:entity_id>/', views.add_review, name='add_review'),
    path('my-reviews/', views.review_list, name='review_list'),
]
