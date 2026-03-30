import uuid
from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Match database columns
    order_code = models.CharField(max_length=20, unique=True, default='')
    customer_name = models.CharField(max_length=100, default='')
    customer_phone = models.CharField(max_length=20, blank=True)
    channel = models.CharField(max_length=50, blank=True, default='')
    items = models.TextField(blank=True, default='')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order_date = models.DateTimeField(null=True, blank=True)
    delivery_address = models.TextField(blank=True, default='')
    delivery_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    delivery_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    vehicle_id = models.UUIDField(null=True, blank=True)
    # Refined: Multiple drivers can be assigned to an order/route team
    drivers = models.ManyToManyField('authentication.User', related_name='assigned_orders', blank=True)
    warehouse_id = models.UUIDField(null=True, blank=True)
    shelf_position = models.CharField(max_length=50, blank=True, null=True, help_text="Format: SHELF-ROW-COL-LEVEL")
    volume = models.DecimalField(max_digits=10, decimal_places=3, default=0.01, help_text="Thể tích (m³)")
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=1.0, help_text="Khối lượng (kg)")
    proof_image = models.TextField(blank=True, default='')
    admin_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_code} - {self.customer_name}"
    
    # Property aliases for backward compatibility
    @property
    def code(self):
        return self.order_code
    
    @property
    def customer_address(self):
        return self.delivery_address
    
    @property
    def delivery_latitude(self):
        return self.delivery_lat
    
    @property
    def delivery_longitude(self):
        return self.delivery_lng
    
    @property
    def priority(self):
        return 'normal'  # Not in database
    
    @property
    def delivered_at(self):
        return None  # Not in database
