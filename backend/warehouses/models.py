import uuid
from django.db import models


class Warehouse(models.Model):
    TYPE_CHOICES = [
        ('main', 'Main Warehouse'),
        ('sub', 'Sub Warehouse'),
        ('transit', 'Transit Point'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    address = models.TextField()
    # Match database column names: lat, lng instead of latitude, longitude
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, db_column='lat')
    lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, db_column='lng')
    # Match database column names: total_volume, used_volume  
    total_volume = models.IntegerField(default=0, help_text='Total volume capacity')
    used_volume = models.IntegerField(default=0, help_text='Used volume')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'warehouses'

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    # Property aliases for backward compatibility with views
    @property
    def latitude(self):
        return self.lat
    
    @property
    def longitude(self):
        return self.lng
    
    @property
    def capacity(self):
        return self.total_volume
    
    @property
    def current_load(self):
        return self.used_volume
    
    @property
    def warehouse_type(self):
        return 'main'  # Default value since column doesn't exist
    
    @property
    def status(self):
        return 'active'  # Default value since column doesn't exist
    
    @property
    def phone(self):
        return ''  # Default value since column doesn't exist
    
    @property
    def email(self):
        return ''  # Default value since column doesn't exist
