from django.contrib import admin
from .models import Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'address', 'total_volume', 'used_volume')
    search_fields = ('code', 'name', 'address')
    ordering = ('code',)