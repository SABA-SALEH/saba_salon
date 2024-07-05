from django.contrib import admin
from .models import Package
# Register your models here.

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'saving_price')
    search_fields = ('name',)
    filter_horizontal = ('services',)
