import uuid
from django.db import models


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('failed_pending', 'Failed - Pending Confirmation'),  # Tài xế báo thất bại, chờ admin xác nhận
        ('failed_confirmed', 'Failed - Confirmed'),  # Admin đã xác nhận thất bại
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.UUIDField()
    order_code = models.CharField(max_length=50)
    driver_id = models.UUIDField(null=True, blank=True)
    driver_name = models.CharField(max_length=100, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    location = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    proof_image = models.TextField(blank=True)  # Base64 or URL
    admin_confirmed = models.BooleanField(default=False)
    admin_confirmed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_code} - {self.driver_name}"
