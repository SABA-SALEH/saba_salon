from django.contrib import admin
from .models import StaffMember
# Register your models here.


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'email')
    search_fields = ('name', 'position', 'email')
