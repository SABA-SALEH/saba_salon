from django.db import models
from django.contrib.auth.models import User
from datetime import time
from checkout.models import Order
import uuid
from packages.models import Package
from reviews.models import Review
from django.apps import apps
from django.db.models import Avg


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)
    
    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.DurationField(null=True, blank=True)
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    available_times = models.JSONField(default=list)

    def __str__(self):
        return self.name

    def get_available_times(self, date):
        """ Returns available time slots for a given date """
        Booking = apps.get_model('services', 'Booking')
        existing_bookings = Booking.objects.filter(service=self, date=date).values_list('time', flat=True)
        available_times = [time_slot for time_slot in self.available_times if time_slot not in existing_bookings]
        return available_times

    def get_average_rating(self):
        """ Calculates and returns the average rating for this service """
        Review = apps.get_model('reviews', 'Review')
        reviews = Review.objects.filter(service=self)
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        return round(average_rating) if average_rating is not None else None
        
        
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)

    def __str__(self):
        if self.service:
            return f'Booking for Service: {self.service.name} by {self.user.username} on {self.date} at {self.time}'
        elif self.package:
            return f'Booking for Package: {self.package.name} by {self.user.username}'
        else:
            return f'Invalid Booking'

    def get_total_cost(self):
        if self.service:
            return self.service.price
        elif self.package:
            return self.package.price
        else:
            return 0
