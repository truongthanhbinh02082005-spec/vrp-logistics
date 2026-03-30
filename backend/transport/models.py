import uuid
from django.db import models


class Route(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    vehicle_id = models.UUIDField(null=True, blank=True)
    # Refined: Multiple drivers per route
    drivers = models.ManyToManyField('authentication.User', related_name='routes', blank=True)
    warehouse_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    original_distance = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Unoptimized Distance in km')
    total_distance = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Distance in km')
    total_time = models.IntegerField(default=0, help_text='Time in minutes')
    total_orders = models.IntegerField(default=0)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'routes'
        ordering = ['-created_at']

    def __str__(self):
        return self.code


class RouteStop(models.Model):
    STOP_TYPE_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
        ('warehouse', 'Warehouse'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('arrived', 'Arrived'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    sequence = models.IntegerField(default=0)
    order_id = models.UUIDField(null=True, blank=True)
    warehouse_id = models.UUIDField(null=True, blank=True)
    stop_type = models.CharField(max_length=20, choices=STOP_TYPE_CHOICES, default='delivery')
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    planned_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)
    distance_from_previous = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    time_from_previous = models.IntegerField(default=0, help_text='Time in minutes')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'route_stops'
        ordering = ['route', 'sequence']

    def __str__(self):
        return f"{self.route.code} - Stop {self.sequence}"
