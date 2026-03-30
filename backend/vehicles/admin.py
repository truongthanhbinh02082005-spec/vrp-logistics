from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('code', 'vehicle_type', 'status', 'capacity_kg', 'capacity_volume')
    list_filter = ('vehicle_type', 'status')
    search_fields = ('code',)
    ordering = ('code',)