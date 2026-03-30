from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Vehicle


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vehicle_list(request):
    if request.method == 'GET':
        vehicles = Vehicle.objects.all()
        data = [{
            'id': str(v.id),
            'code': v.code,
            'vehicle_type': v.vehicle_type,
            'brand': '',
            'model': '',
            'capacity': v.capacity_kg,
            'volume_capacity': float(v.capacity_volume) if v.capacity_volume else 0,
            'current_load': 0,
            'fuel_type': 'diesel',
            'fuel_consumption': 0,
            'status': v.status,
            'current_latitude': float(v.current_lat) if v.current_lat else None,
            'current_longitude': float(v.current_lng) if v.current_lng else None,
            'is_assigned': v.assigned_drivers.exists(),
        } for v in vehicles]
        return Response(data)

    elif request.method == 'POST':
        vehicle = Vehicle.objects.create(
            code=request.data.get('code'),
            vehicle_type=request.data.get('vehicle_type', 'truck'),
            capacity_kg=request.data.get('capacity', 0),
            capacity_volume=request.data.get('volume_capacity', 0),
            status=request.data.get('status', 'available'),
        )
        return Response({
            'id': str(vehicle.id),
            'code': vehicle.code,
            'message': 'Vehicle created successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def vehicle_detail(request, pk):
    try:
        vehicle = Vehicle.objects.get(pk=pk)
    except Vehicle.DoesNotExist:
        return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({
            'id': str(vehicle.id),
            'code': vehicle.code,
            'vehicle_type': vehicle.vehicle_type,
            'brand': '',
            'model': '',
            'capacity': vehicle.capacity_kg,
            'volume_capacity': float(vehicle.capacity_volume) if vehicle.capacity_volume else 0,
            'current_load': 0,
            'fuel_type': 'diesel',
            'fuel_consumption': 0,
            'status': vehicle.status,
            'current_latitude': float(vehicle.current_lat) if vehicle.current_lat else None,
            'current_longitude': float(vehicle.current_lng) if vehicle.current_lng else None,
        })

    elif request.method == 'PUT':
        vehicle.code = request.data.get('code', vehicle.code)
        vehicle.vehicle_type = request.data.get('vehicle_type', vehicle.vehicle_type)
        vehicle.capacity_kg = request.data.get('capacity', vehicle.capacity_kg)
        vehicle.capacity_volume = request.data.get('volume_capacity', vehicle.capacity_volume)
        vehicle.status = request.data.get('status', vehicle.status)
        vehicle.save()
        return Response({'message': 'Vehicle updated successfully'})

    elif request.method == 'DELETE':
        vehicle.delete()
        return Response({'message': 'Vehicle deleted successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_vehicles(request):
    """Danh sách xe có thể sử dụng"""
    vehicles = Vehicle.objects.filter(status='available')
    data = [{
        'id': str(v.id),
        'code': v.code,
        'vehicle_type': v.vehicle_type,
        'capacity': v.capacity_kg,
    } for v in vehicles]
    return Response(data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_vehicle_location(request, pk):
    """Cập nhật vị trí xe"""
    try:
        vehicle = Vehicle.objects.get(pk=pk)
    except Vehicle.DoesNotExist:
        return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

    vehicle.current_lat = request.data.get('latitude')
    vehicle.current_lng = request.data.get('longitude')
    vehicle.save()
    return Response({'message': 'Location updated successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pack_orders(request):
    """
    Bin Packing API - Xếp đơn hàng vào xe tối ưu
    Uses First Fit Decreasing algorithm
    """
    from .bin_packing import first_fit_decreasing
    from orders.models import Order
    
    order_ids = request.data.get('order_ids', [])
    vehicle_ids = request.data.get('vehicle_ids', [])
    
    if not order_ids:
        return Response({'error': 'No orders provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not vehicle_ids:
        return Response({'error': 'No vehicles provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get orders
    orders = Order.objects.filter(id__in=order_ids)
    orders_data = []
    for o in orders:
        # Estimate weight from amount if not available
        weight = getattr(o, 'weight', None) or float(o.amount) / 100 if o.amount else 1
        orders_data.append({
            'id': str(o.id),
            'code': o.order_code,
            'weight': weight,
            'volume': 0.1,  # Default volume
        })
    
    # Get vehicles
    vehicles = Vehicle.objects.filter(id__in=vehicle_ids)
    vehicles_data = [{
        'id': str(v.id),
        'code': v.code,
        'capacity_kg': v.capacity_kg if v.capacity_kg > 0 else 1000,
        'capacity_volume': float(v.capacity_volume) if v.capacity_volume else 100,
    } for v in vehicles]
    
    # Run bin packing algorithm
    result = first_fit_decreasing(orders_data, vehicles_data)
    
    return Response({
        'message': 'Bin packing completed',
        'algorithm': 'First Fit Decreasing (FFD)',
        'summary': result['summary'],
        'assignments': result['assignments'],
        'unassigned': result['unassigned'],
    })
