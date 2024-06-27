from django.contrib import admin
from .models import Service, Category, Booking

class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'duration',
        'rating',
        'image',
        'available_times',
    )
    ordering = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'service',
        'date',
        'time',
        'created_at',
    )
    list_filter = (
        'date',
        'time',
        'service',
    )

admin.site.register(Service, ServiceAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Booking, BookingAdmin)
