from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Warehouse


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def warehouse_list(request):
    if request.method == 'GET':
        warehouses = Warehouse.objects.all()
        data = [{
            'id': str(w.id),
            'code': w.code,
            'name': w.name,
            'address': w.address,
            'latitude': float(w.lat) if w.lat else None,
            'longitude': float(w.lng) if w.lng else None,
            'capacity': w.total_volume,
            'current_load': w.used_volume,
            'warehouse_type': 'main',
            'status': 'active',
            'phone': '',
            'email': '',
        } for w in warehouses]
        return Response(data)

    elif request.method == 'POST':
        warehouse = Warehouse.objects.create(
            code=request.data.get('code'),
            name=request.data.get('name'),
            address=request.data.get('address'),
            lat=request.data.get('latitude'),
            lng=request.data.get('longitude'),
            total_volume=request.data.get('capacity', 0),
        )
        return Response({
            'id': str(warehouse.id),
            'code': warehouse.code,
            'name': warehouse.name,
            'message': 'Warehouse created successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def warehouse_detail(request, pk):
    try:
        warehouse = Warehouse.objects.get(pk=pk)
    except Warehouse.DoesNotExist:
        return Response({'error': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({
            'id': str(warehouse.id),
            'code': warehouse.code,
            'name': warehouse.name,
            'address': warehouse.address,
            'latitude': float(warehouse.lat) if warehouse.lat else None,
            'longitude': float(warehouse.lng) if warehouse.lng else None,
            'capacity': warehouse.total_volume,
            'current_load': warehouse.used_volume,
            'warehouse_type': 'main',
            'status': 'active',
            'phone': '',
            'email': '',
        })

    elif request.method == 'PUT':
        warehouse.name = request.data.get('name', warehouse.name)
        warehouse.address = request.data.get('address', warehouse.address)
        warehouse.lat = request.data.get('latitude', warehouse.lat)
        warehouse.lng = request.data.get('longitude', warehouse.lng)
        warehouse.total_volume = request.data.get('capacity', warehouse.total_volume)
        warehouse.save()
        return Response({'message': 'Warehouse updated successfully'})

    elif request.method == 'DELETE':
        warehouse.delete()
        return Response({'message': 'Warehouse deleted successfully'})
