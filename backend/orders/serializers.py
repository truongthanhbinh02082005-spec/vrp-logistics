from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'code',
            'customer_name',
            'customer_phone',
            'customer_email',
            'customer_address',
            'delivery_latitude',
            'delivery_longitude',
            'weight',
            'volume',
            'quantity',
            'description',
            'status',
            'priority',
            'warehouse_id',
            'vehicle_id',
            'driver_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
