from django.contrib import admin
from .models import Order
from services.models import Booking

class BookingInline(admin.TabularInline):
    model = Booking
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    inlines = [BookingInline]
    readonly_fields = ('order_number', 'date', 'order_total', 'grand_total')
    fields = ('order_number', 'date', 'full_name', 'email', 'phone_number', 'order_total', 'grand_total')
    list_display = ('order_number', 'date', 'full_name', 'order_total', 'grand_total')
    ordering = ('-date',)

admin.site.register(Order, OrderAdmin)
