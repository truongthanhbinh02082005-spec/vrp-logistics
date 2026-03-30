from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    capacity = serializers.ReadOnlyField(source='capacity_kg')
    volume_capacity = serializers.ReadOnlyField(source='capacity_volume')
    brand = serializers.ReadOnlyField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'code', 'vehicle_type', 'capacity', 'volume_capacity',
            'brand', 'status', 'current_latitude', 'current_longitude',
            'driver_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
