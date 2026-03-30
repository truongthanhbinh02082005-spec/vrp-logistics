from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Transaction


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    if request.method == 'GET':
        transactions = Transaction.objects.all()
        data = [{
            'id': str(t.id),
            'order_id': str(t.order_id) if t.order_id else None,
            'order_code': t.order_code,
            'driver_id': str(t.driver_id) if t.driver_id else None,
            'driver_name': t.driver_name,
            'completed_at': t.completed_at.isoformat() if t.completed_at else None,
            'location': t.location,
            'status': t.status,
            'proof_image': t.proof_image,
            'admin_confirmed': t.admin_confirmed,
            'notes': t.notes,
            'created_at': t.created_at.isoformat() if t.created_at else None,
        } for t in transactions]
        return Response(data)

    elif request.method == 'POST':
        transaction = Transaction.objects.create(
            order_id=request.data.get('order_id'),
            order_code=request.data.get('order_code', ''),
            driver_id=request.data.get('driver_id'),
            driver_name=request.data.get('driver_name', ''),
            completed_at=timezone.now(),
            location=request.data.get('location', ''),
            proof_image=request.data.get('proof_image', ''),
            notes=request.data.get('notes', ''),
            status='pending',
        )
        return Response({
            'id': str(transaction.id),
            'message': 'Transaction created successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def transaction_detail(request, pk):
    try:
        transaction = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({
            'id': str(transaction.id),
            'order_id': str(transaction.order_id) if transaction.order_id else None,
            'order_code': transaction.order_code,
            'driver_id': str(transaction.driver_id) if transaction.driver_id else None,
            'driver_name': transaction.driver_name,
            'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None,
            'location': transaction.location,
            'status': transaction.status,
            'proof_image': transaction.proof_image,
            'admin_confirmed': transaction.admin_confirmed,
        })

    elif request.method == 'PUT':
        transaction.status = request.data.get('status', transaction.status)
        transaction.notes = request.data.get('notes', transaction.notes)
        transaction.save()
        return Response({'message': 'Transaction updated successfully'})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def confirm_transaction(request, pk):
    """Admin xác nhận giao dịch (bao gồm xác nhận thất bại)"""
    try:
        transaction = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

    old_status = transaction.status
    
    transaction.admin_confirmed = True
    transaction.admin_confirmed_at = timezone.now()
    
    # Xử lý case xác nhận THẤT BẠI
    if old_status == 'failed_pending':
        transaction.status = 'failed_confirmed'
        transaction.save()
        
        # Cộng thể tích về kho (order đã là failed từ khi tài xế báo)
        try:
            from orders.models import Order
            from warehouses.models import Warehouse
            
            order = Order.objects.get(pk=transaction.order_id)
            
            # Cộng thể tích về kho
            if order.warehouse_id:
                warehouse = Warehouse.objects.get(pk=order.warehouse_id)
                order_volume = float(order.volume) if order.volume else 0
                warehouse.used_volume = warehouse.used_volume + int(order_volume * 1000)
                warehouse.save()
                print(f"[WAREHOUSE] Admin confirmed failed: Order {order.order_code} +{order_volume}m³ to {warehouse.name}")
                
        except Exception as e:
            print(f"Error processing failed confirmation: {e}")
            
    else:
        # Xử lý case xác nhận GIAO THÀNH CÔNG (logic cũ)
        transaction.status = 'confirmed'
        transaction.save()

    # Auto-complete associated Route if all its orders are delivered/failed AND ALL transactions are confirmed
    msg = 'Transaction confirmed successfully'
    if old_status == 'failed_pending':
        msg = 'Đã xác nhận thất bại - Thể tích đã được cộng lại vào kho'

    try:
        from transport.models import Route, RouteStop
        
        order_id = transaction.order_id
        if order_id:
            route_stop = RouteStop.objects.filter(order_id=order_id).first()
            if route_stop:
                route = route_stop.route
                
                # Check if all stops are done by driver
                driver_remaining_stops = RouteStop.objects.filter(
                    route=route
                ).exclude(status__in=['completed', 'skipped']).count()
                
                # Check if all transactions for this route are confirmed by admin
                route_order_ids = RouteStop.objects.filter(
                    route=route, stop_type='delivery'
                ).values_list('order_id', flat=True)
                
                unconfirmed_transactions = Transaction.objects.filter(
                    order_id__in=route_order_ids,
                    admin_confirmed=False
                ).count()
                
                if driver_remaining_stops == 0 and unconfirmed_transactions == 0:
                    # Tất cả stops đã xong và admin đã xác nhận hết -> Mark route as completed
                    route.status = 'completed'
                    route.actual_end_time = timezone.now()
                    route.save()
                    print(f"[ROUTE] Auto-completed route {route.code} after ALL transactions confirmed")
                    
                    # Cập nhật status xe thành available
                    if route.vehicle_id:
                        try:
                            from vehicles.models import Vehicle
                            vehicle = Vehicle.objects.get(pk=route.vehicle_id)
                            vehicle.status = 'available'
                            vehicle.save()
                        except:
                            pass
    except Exception as e:
        print(f"Error auto-completing route: {e}")

    return Response({'message': msg})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_transactions(request):
    """Danh sách giao dịch chờ xác nhận"""
    transactions = Transaction.objects.filter(admin_confirmed=False)
    data = [{
        'id': str(t.id),
        'order_code': t.order_code,
        'driver_name': t.driver_name,
        'completed_at': t.completed_at.isoformat() if t.completed_at else None,
        'location': t.location,
        'proof_image': t.proof_image,
    } for t in transactions]
    return Response(data)
