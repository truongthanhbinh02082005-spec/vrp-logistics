from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'customer_name', 'status', 'amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_code', 'customer_name', 'customer_phone', 'delivery_address')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'