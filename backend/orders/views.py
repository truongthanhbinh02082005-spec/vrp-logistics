from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Order


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list(request):
    if request.method == 'GET':
        status_filter = request.query_params.get('status')

        orders = Order.objects.all()

        if status_filter:
            orders = orders.filter(status=status_filter)

        data = [{
            'id': str(o.id),
            'code': o.order_code,
            'customer_name': o.customer_name,
            'customer_phone': o.customer_phone,
            'customer_address': o.delivery_address,
            'delivery_latitude': float(o.delivery_lat) if o.delivery_lat else None,
            'delivery_longitude': float(o.delivery_lng) if o.delivery_lng else None,
            'weight': 0,
            'volume': 0,
            'quantity': 1,
            'status': o.status,
            'priority': 'normal',
            'cod_amount': float(o.amount) if o.amount else 0,
            'shipping_fee': 0,
            'notes': o.items,
            'drivers': [{
                'id': str(d.id),
                'full_name': d.full_name or d.username
            } for d in o.drivers.all()],
            'created_at': o.created_at.isoformat() if o.created_at else None,
        } for o in orders]
        return Response(data)

    elif request.method == 'POST':
        code = request.data.get('code')
        if not code:
            import uuid
            code = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        # Prepare items content (handle JSON column requirement)
        import json
        raw_notes = request.data.get('notes', '')
        items_content = raw_notes
        try:
            if isinstance(raw_notes, (list, dict)):
                items_content = json.dumps(raw_notes)
            else:
                # If string, try to load to check validity, if fail, wrap it
                try:
                    json.loads(raw_notes)
                    items_content = raw_notes # It is valid json string
                except ValueError:
                    # Treat as plain text, wrap in object
                    items_content = json.dumps([{"name": str(raw_notes), "quantity": 1}])
        except Exception:
            items_content = json.dumps([])

        order = Order.objects.create(
            order_code=code,
            customer_name=request.data.get('customer_name', '') or 'Khách lẻ', # Fallback if empty
            customer_phone=request.data.get('customer_phone', '') or '',
            delivery_address=request.data.get('customer_address', '') or '',
            delivery_lat=request.data.get('delivery_latitude'),
            delivery_lng=request.data.get('delivery_longitude'),
            amount=request.data.get('cod_amount', 0),
            order_date=timezone.now(),
            items=items_content,
            warehouse_id=request.data.get('warehouse_id'),
        )
        
        # --- AUTO SLOTTING (Kho đã được user chọn tay) ---
        try:
            from .slotting import auto_assign_slot
            if order.warehouse_id:
                auto_assign_slot(order)
        except Exception as e:
            print(f"Slotting Error: {e}")
        # ---------------------

        return Response({
            'id': str(order.id),
            'code': order.order_code,
            'customer_name': order.customer_name,
            'message': 'Order created successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_orders(request):
    """
    API tạo nhiều đơn hàng cùng lúc (bulk insert) - Tối ưu performance
    Payload: { orders: [...], warehouse_id: "..." }
    """
    import json
    import uuid
    
    orders_data = request.data.get('orders', [])
    warehouse_id = request.data.get('warehouse_id')
    
    print(f"[BULK] Received {len(orders_data)} orders, warehouse_id={warehouse_id}")
    
    if not orders_data:
        return Response({'error': 'No orders provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not warehouse_id:
        return Response({'error': 'warehouse_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    created_orders = []
    errors = []
    
    for idx, item in enumerate(orders_data):
        try:
            code = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            # Handle notes/items
            raw_notes = item.get('notes', '')
            items_content = json.dumps([{"name": str(raw_notes) if raw_notes else "Hàng hóa", "quantity": 1}])
            
            order = Order.objects.create(
                order_code=code,
                customer_name=item.get('customer_name', 'Khách lẻ') or 'Khách lẻ',
                customer_phone=str(item.get('customer_phone', '')),
                delivery_address=item.get('customer_address', ''),
                delivery_lat=item.get('delivery_latitude'),
                delivery_lng=item.get('delivery_longitude'),
                amount=float(item.get('cod_amount', 0) or 0),
                weight=float(item.get('weight', 1.0) or 1.0),
                volume=float(item.get('volume', 0.01) or 0.01),
                order_date=timezone.now(),
                items=items_content,
                warehouse_id=warehouse_id,
            )
            
            created_orders.append({'id': str(order.id), 'code': order.order_code})
            
        except Exception as e:
            errors.append({'index': idx, 'error': str(e)})
            print(f"[BULK] Error at index {idx}: {e}")
    
    print(f"[BULK] Result: {len(created_orders)} success, {len(errors)} failed")
    
    # Cập nhật used_volume của kho sau khi import
    if created_orders and warehouse_id:
        try:
            from warehouses.models import Warehouse
            from django.db.models import Sum
            
            warehouse = Warehouse.objects.get(pk=warehouse_id)
            # Tính tổng volume từ các đơn hàng trong kho
            total_used = Order.objects.filter(
                warehouse_id=warehouse_id,
                status__in=['pending', 'confirmed', 'assigned']
            ).aggregate(Sum('volume'))['volume__sum'] or 0
            
            # Cập nhật used_volume (chuyển m³ sang đơn vị của kho nếu cần, warehouse dùng dm³ * 1000)
            warehouse.used_volume = int(float(total_used) * 1000)
            warehouse.save()
            print(f"[BULK] Updated warehouse {warehouse.name} used_volume: {warehouse.used_volume}")
        except Exception as e:
            print(f"[BULK] Error updating warehouse volume: {e}")
    
    return Response({
        'success': len(created_orders),
        'failed': len(errors),
        'total': len(orders_data),
        'message': f'Bulk import completed: {len(created_orders)} success, {len(errors)} failed'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({
            'id': str(order.id),
            'code': order.order_code,
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'customer_email': '',
            'customer_address': order.delivery_address,
            'delivery_latitude': float(order.delivery_lat) if order.delivery_lat else None,
            'delivery_longitude': float(order.delivery_lng) if order.delivery_lng else None,
            'weight': 0,
            'volume': 0,
            'quantity': 1,
            'description': order.items,
            'status': order.status,
            'priority': 'normal',
            'notes': order.items,
            'cod_amount': float(order.amount) if order.amount else 0,
            'shipping_fee': 0,
            'drivers': [{
                'id': str(d.id),
                'full_name': d.full_name or d.username
            } for d in order.drivers.all()],
        })

    elif request.method == 'PUT':
        order.customer_name = request.data.get('customer_name', order.customer_name)
        order.customer_phone = request.data.get('customer_phone', order.customer_phone)
        order.delivery_address = request.data.get('customer_address', order.delivery_address)
        order.delivery_lat = request.data.get('delivery_latitude', order.delivery_lat)
        order.delivery_lng = request.data.get('delivery_longitude', order.delivery_lng)
        order.items = request.data.get('notes', order.items)
        order.status = request.data.get('status', order.status)
        order.save()
        return Response({'message': 'Order updated successfully'})

    elif request.method == 'DELETE':
        order.delete()
        return Response({'message': 'Order deleted successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_orders(request):
    """Danh sách đơn hàng chờ xử lý"""
    orders = Order.objects.filter(status='pending')
    data = [{
        'id': str(o.id),
        'code': o.order_code,
        'customer_name': o.customer_name,
        'customer_address': o.delivery_address,
        'priority': 'normal',
        'weight': 0,
        'warehouse_id': str(o.warehouse_id) if o.warehouse_id else None,
    } for o in orders]
    return Response(data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, pk):
    """Cập nhật trạng thái đơn hàng - Tự động điều chỉnh thể tích kho"""
    from warehouses.models import Warehouse
    
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    old_status = order.status
    new_status = request.data.get('status')
    
    if new_status:
        order.status = new_status
        order.save()
        
        # Điều chỉnh thể tích kho dựa trên trạng thái
        if order.warehouse_id:
            try:
                warehouse = Warehouse.objects.get(pk=order.warehouse_id)
                order_volume = float(order.volume) if order.volume else 0
                
                # Đơn được lên giao (in_transit) -> Hàng rời kho -> Trừ thể tích
                if new_status == 'in_transit' and old_status != 'in_transit':
                    warehouse.used_volume = max(0, warehouse.used_volume - int(order_volume * 1000))
                    warehouse.save()
                    print(f"[WAREHOUSE] Order {order.order_code} shipped: -{order_volume}m³ from {warehouse.name}")
                    
                # Đơn giao thất bại (failed) từ in_transit -> Hàng về kho -> Cộng thể tích
                if new_status == 'failed' and old_status == 'in_transit':
                    warehouse.used_volume = warehouse.used_volume + int(order_volume * 1000)
                    warehouse.save()
                    print(f"[WAREHOUSE] Order {order.order_code} failed: +{order_volume}m³ to {warehouse.name}")
                    
            except Warehouse.DoesNotExist:
                pass
        
        return Response({'message': 'Order status updated successfully'})
    return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def assign_order(request, pk):
    """Gán đơn hàng cho xe và tài xế"""
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    order.vehicle_id = request.data.get('vehicle_id')
    driver_ids = request.data.get('driver_ids', [])
    if driver_ids:
        order.drivers.set(driver_ids)
    elif request.data.get('driver_id'):
        # Backward compatibility for single ID
        order.drivers.set([request.data.get('driver_id')])
    
    order.status = 'assigned'
    order.save()
    return Response({'message': 'Order assigned successfully'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_orders(request):
    """Xóa tất cả đơn hàng chưa giao (giữ lại đơn đã giao)"""
    # Chỉ xóa các đơn chưa hoàn thành
    orders_to_delete = Order.objects.exclude(status__in=['delivered', 'completed'])
    count = orders_to_delete.count()
    orders_to_delete.delete()
    return Response({'message': f'Đã xóa {count} đơn hàng (giữ lại đơn đã giao)', 'deleted_count': count})


@api_view(['GET'])
def warehouse_stats(request, warehouse_id):
    """
    API Dashboard: Trả về % lấp đầy của từng kệ trong kho
    """
    from .slotting import WAREHOUSE_LAYOUT
    
    stats = {}
    total_capacity = 0
    total_used = 0
    
    for shelf, dims in WAREHOUSE_LAYOUT.items():
        total_slots = dims['rows'] * dims['cols'] * dims['levels']
        
        # Count orders in this shelf for this warehouse
        # Filter items that START with "{shelf}-" e.g. "A-"
        used_slots = Order.objects.filter(
            warehouse_id=warehouse_id,
            shelf_position__startswith=f"{shelf}-",
            status__in=['pending', 'confirmed', 'assigned']
        ).count()
        
        stats[shelf] = {
            'total': total_slots,
            'used': used_slots,
            'percent': int((used_slots / total_slots) * 100) if total_slots > 0 else 0
        }
        total_capacity += total_slots
        total_used += used_slots

    return Response({
        'shelves': stats,
        'summary': {
             'total_capacity_slots': total_capacity,
             'total_used_slots': total_used,
             'occupancy_rate': int((total_used/total_capacity)*100) if total_capacity > 0 else 0
        }
    })

@api_view(['GET'])
def warehouse_capacity(request, warehouse_id):
    """
    API check sức chứa còn lại của kho theo VOLUME (m³)
    """
    from warehouses.models import Warehouse
    from django.db.models import Sum
    
    try:
        warehouse = Warehouse.objects.get(pk=warehouse_id)
    except Warehouse.DoesNotExist:
        return Response({'error': 'Warehouse not found'}, status=404)
    
    total_volume = float(warehouse.total_volume or 0)  # m³
    
    # Tính tổng volume đang dùng từ các đơn hàng trong kho
    used_volume_result = Order.objects.filter(
        warehouse_id=warehouse_id,
        status__in=['pending', 'confirmed', 'assigned']
    ).aggregate(Sum('volume'))
    
    used_volume = float(used_volume_result['volume__sum'] or 0)
    remaining_volume = total_volume - used_volume
    
    return Response({
        'warehouse_id': str(warehouse_id),
        'warehouse_name': warehouse.name,
        'total_volume': total_volume,
        'used_volume': round(used_volume, 3),
        'remaining_volume': round(remaining_volume, 3),
        'occupancy_rate': round((used_volume / total_volume) * 100, 1) if total_volume > 0 else 0,
        'is_full': remaining_volume <= 0
    })
