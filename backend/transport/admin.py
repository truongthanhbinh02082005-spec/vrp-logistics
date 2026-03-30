from django.contrib import admin
from .models import Route, RouteStop


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('code', 'status', 'total_orders', 'total_distance', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('code',)
    ordering = ('-created_at',)


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('route', 'sequence', 'stop_type', 'status', 'address')
    list_filter = ('stop_type', 'status')
    ordering = ('route', 'sequence')