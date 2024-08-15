from django.contrib import admin
from .models import Service, Category, Booking


class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'duration',
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
        'get_service_name',
        'get_package_name',
        'date',
        'time',
        'created_at',
        'get_order_number',
    )
    list_filter = (
        'date',
        'time',
        'service',
        'package',
        'order',
    )

    def get_service_name(self, obj):
        return obj.service.name if obj.service else None
    get_service_name.short_description = 'Service'

    def get_package_name(self, obj):
        return obj.package.name if obj.package else None
    get_package_name.short_description = 'Package'

    def get_order_number(self, obj):
        return obj.order.order_number if obj.order else None
    get_order_number.short_description = 'Order Number'


admin.site.register(Service, ServiceAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Booking, BookingAdmin)
