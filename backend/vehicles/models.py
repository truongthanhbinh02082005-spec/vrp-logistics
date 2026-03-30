import uuid
from django.db import models


class Vehicle(models.Model):
    TYPE_CHOICES = [
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('motorcycle', 'Motorcycle'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Match database columns
    code = models.CharField(max_length=20, unique=True, default='')
    vehicle_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='truck')
    capacity_kg = models.IntegerField(default=0, help_text='Capacity in kg')
    capacity_volume = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Volume in m3')
    # driver_id has been moved to User.vehicle
    # driver_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    current_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    cost_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicles'

    def __str__(self):
        return f"{self.code}"
    
    # Property aliases for backward compatibility with frontend/views
    @property
    def capacity(self):
        return self.capacity_kg
    
    @property
    def volume_capacity(self):
        return self.capacity_volume
    
    @property
    def brand(self):
        return ''
    
    @property
    def current_latitude(self):
        return self.current_lat
    
    @property
    def current_longitude(self):
        return self.current_lng
