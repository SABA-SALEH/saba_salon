from django.db import models
from django.contrib.auth.models import User
from datetime import time

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
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    available_times = models.JSONField(default=list)  

    def __str__(self):
        return self.name
    
    def get_available_times(self, date):
        """ Returns available time slots for a given date """
        existing_bookings = Booking.objects.filter(service=self, date=date).values_list('time', flat=True)
        available_times = [time_slot for time_slot in self.available_times if time_slot not in existing_bookings]
        return available_times


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Booking for {self.service.name} by {self.user.username} on {self.date} at {self.time}'
