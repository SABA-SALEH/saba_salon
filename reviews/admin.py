from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'package', 'rating', 'created_at')
    list_filter = ('created_at', 'rating')
    search_fields = ('user__username', 'service__name', 'package__name')
