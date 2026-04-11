from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    full_name = request.data.get('full_name', '')
    phone = request.data.get('phone', '')
    role = request.data.get('role', 'driver')

    if not username or not email or not password:
        return Response({'error': 'Username, email and password required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        phone=phone,
        role=role
    )

    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user

    if request.method == 'GET':
        return Response({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'role': user.role,
            'avatar': user.avatar if user.avatar else None
        })

    elif request.method == 'PUT':
        user.full_name = request.data.get('full_name', user.full_name)
        user.phone = request.data.get('phone', user.phone)
        user.email = request.data.get('email', user.email)
        user.save()

        return Response({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'role': user.role
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'})
    except:
        return Response({'message': 'Logout successful'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    """Danh sách users (chỉ admin/manager)"""
    if request.user.role not in ['admin', 'manager']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    users = User.objects.all()
    data = [{
        'id': str(u.id),
        'username': u.username,
        'email': u.email,
        'full_name': u.full_name,
        'phone': u.phone,
        'role': u.role,
        'status': u.status,
    } for u in users]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_list(request):
    """Danh sách tài xế kèm thông tin xe"""
    from transport.models import Route
    
    drivers = User.objects.filter(role='driver')
    
    # Lấy danh sách driver_id đang có lộ trình chưa hoàn thành (pending hoặc in_progress)
    active_driver_ids = set(
        Route.objects.filter(
            status__in=['pending', 'in_progress']
        ).values_list('drivers__id', flat=True)
    )
    # Loại bỏ None (nếu route không có driver nào)
    active_driver_ids.discard(None)
    
    data = []
    for d in drivers:
        data.append({
            'id': str(d.id),
            'username': d.username,
            'full_name': d.full_name,
            'phone': d.phone,
            'email': d.email,
            'status': d.status,
            'current_vehicle': d.vehicle.code if d.vehicle else None,
            'current_vehicle_id': str(d.vehicle.id) if d.vehicle else None,
            'has_active_route': d.id in active_driver_ids,
        })
        
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_current_order(request):
    """Lấy thông tin lộ trình hiện tại của tài xế"""
    from transport.models import Route, RouteStop
    from orders.models import Order
    from vehicles.models import Vehicle

    # 1. Find active route
    try:
        current_route = Route.objects.filter(
            drivers=request.user
        ).order_by('-created_at').first()
        
        # If route is completed/cancelled, ignore it
        if current_route and current_route.status in ['completed', 'cancelled']:
            current_route = None
            
    except Exception:
        current_route = None

    stops = []
    
    # CASE A: Route Exists -> Try to get RouteStops
    if current_route:
        stops = RouteStop.objects.filter(route=current_route).order_by('sequence')
        # CRITICAL FIX: If Route exists but has NO stops (Zombie route), treat as no route
        if not stops:
            current_route = None

    # CASE B: No Route (or Zombie Route) -> Look for Ad-hoc Assigned Orders (Fallback)
    if not current_route:
        assigned_orders = Order.objects.filter(
            drivers=request.user,
            status__in=['assigned', 'in_transit']
        )
        if not assigned_orders:
             return Response({'message': 'No active route or orders'}, status=status.HTTP_404_NOT_FOUND)
             
        # Create virtual stops from orders
        current_route = type('obj', (object,), {
            'id': 'virtual',
            'code': 'ADHOC-ROUTE',
            'vehicle_id': assigned_orders[0].vehicle_id if assigned_orders else None
        })
        
        # Convert Orders to "Virtual Stops" on the fly
        stops = [] # Reset to be specific
        for idx, o in enumerate(assigned_orders):
            stops.append(type('obj', (object,), {
                'id': f'virtual-{o.id}',
                'sequence': idx + 1,
                'order_id': o.id,
                'address': o.delivery_address,
                'latitude': o.delivery_lat,
                'longitude': o.delivery_lng,
                'status': 'pending' if o.status == 'assigned' else 'pending',
                'stop_type': 'delivery',
                'planned_arrival': None,
                'distance_from_previous': 0
            }))

    stops_data = []
    completed_count = 0
    pending_count = 0
    
    # Pre-fetch orders for Case A (Case B already has them, but let's be uniform)
    if not isinstance(stops, list): # It's a QuerySet from Case A
        order_ids = [s.order_id for s in stops if s.order_id]
        orders_qs = Order.objects.filter(id__in=order_ids)
        order_map = {o.id: o for o in orders_qs}
    else: # Case B Virtual List
        orders_qs = Order.objects.filter(id__in=[s.order_id for s in stops])
        order_map = {o.id: o for o in orders_qs}

    for s in stops:
        # Determine Status
        s_status = getattr(s, 'status', 'pending')
        
        if s_status == 'completed':
            completed_count += 1
        elif s_status != 'skipped':
            pending_count += 1

        order = order_map.get(s.order_id)
        
        # Format ETA
        eta = "00:00"
        planned = getattr(s, 'planned_arrival', None)
        if planned:
            eta = planned.strftime('%H:%M')
        
        # Format Distance
        dist_val = getattr(s, 'distance_from_previous', 0)
        dist = f"{float(dist_val):.1f} km" if dist_val else "0 km"

        # Coords
        lat = getattr(s, 'latitude', None)
        lng = getattr(s, 'longitude', None)
        stop_type = getattr(s, 'stop_type', 'delivery')

        stops_data.append({
            'id': str(getattr(s, 'id', '')),
            'sequence': getattr(s, 'sequence', 0),
            'address': getattr(s, 'address', '') or (order.delivery_address if order else "Kho"),
            'order_id': str(s.order_id) if s.order_id else None,
            'order_code': order.order_code if order else f"STOP-{getattr(s, 'sequence', 0)}",
            'customer_name': order.customer_name if order else "",
            'customer_phone': order.customer_phone if order else "",
            'items': order.items if order else "",
            'lat': float(lat) if lat else None,
            'lng': float(lng) if lng else None,
            'status': s_status,
            'eta': eta,
            'distance': dist,
            'stop_type': stop_type
        })

    # 5. Determine "Current Stop"
    remaining_stops = [s for s in stops_data if s['status'] not in ['completed', 'skipped']]
    current_stop = remaining_stops[0] if remaining_stops else None
    upcoming_list = remaining_stops[1:] if remaining_stops else []
    
    # 6. Vehicle Info
    vehicle_info = {}
    v_id = getattr(current_route, 'vehicle_id', None)
    if v_id:
        try:
             vehicle = Vehicle.objects.get(id=v_id)
             vehicle_info = {
                 'plate': vehicle.code,
                 'code': vehicle.code
             }
        except:
             pass

    # 7. Warehouse Info (for navigation from depot)
    warehouse_info = {}
    try:
        from warehouses.models import Warehouse
        # Get first warehouse or the one associated with the route
        wh = Warehouse.objects.first()
        if wh:
            warehouse_info = {
                'name': wh.name,
                'lat': float(wh.latitude) if wh.latitude else None,
                'lng': float(wh.longitude) if wh.longitude else None,
                'address': getattr(wh, 'address', '')
            }
    except Exception as e:
        print(f"Error getting warehouse: {e}")

    return Response({
        'route_id': str(getattr(current_route, 'id', 'virtual')),
        'route_code': getattr(current_route, 'code', 'ADHOC'),
        'current_stop': current_stop,
        'upcoming_stops': upcoming_list,
        'all_remaining_stops': remaining_stops,  # Full list for navigation
        'warehouse': warehouse_info,
        'stats': {
            'completed': completed_count,
            'remaining': pending_count,
            'on_time_rate': 94
        },
        'vehicle': vehicle_info
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def driver_orders(request):
    """Lấy tất cả đơn hàng của tài xế"""
    from orders.models import Order
    
    orders = Order.objects.filter(drivers=request.user)
    data = [{
        'id': str(o.id),
        'order_code': o.order_code,
        'customer_name': o.customer_name,
        'delivery_address': o.delivery_address,
        'status': o.status,
    } for o in orders]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_delivery(request):
    """Tài xế xác nhận đã giao hàng và upload ảnh"""
    from orders.models import Order
    from transactions.models import Transaction
    from transport.models import RouteStop
    from django.utils import timezone
    
    order_id = request.data.get('order_id')
    proof_image = request.data.get('proof_image', '')
    
    if not order_id:
        return Response({'error': 'Order ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(pk=order_id, drivers=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update order status
    order.status = 'delivered'
    order.save()
    
    # Update RouteStop status to completed (để đơn tiếp theo nhảy lên)
    try:
        route_stop = RouteStop.objects.filter(order_id=order_id).first()
        if route_stop:
            route_stop.status = 'completed'
            route_stop.save()
    except Exception as e:
        print(f"Error updating RouteStop: {e}")
    
    # KHÔNG auto-complete route ở đây - chờ admin xác nhận ở Lịch sử giao dịch
    
    # Create transaction record (chờ admin xác nhận)
    Transaction.objects.create(
        order_id=order.id,
        order_code=order.order_code,
        driver_id=request.user.id,
        driver_name=request.user.full_name or request.user.username,
        completed_at=timezone.now(),
        location=order.delivery_address,
        proof_image=proof_image,
        status='pending',
    )
    
    return Response({'message': 'Delivery confirmed successfully'})

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    """Chi tiết user: Cập nhật hoặc Xóa (Admin only)"""
    if request.user.role not in ['admin', 'manager']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        user.full_name = request.data.get('full_name', user.full_name)
        user.phone = request.data.get('phone', user.phone)
        user.email = request.data.get('email', user.email)
        status_val = request.data.get('status')
        if status_val:
            user.status = status_val
        
        # Admin reset password
        new_password = request.data.get('password')
        if new_password:
            user.set_password(new_password)
            
        user.save()

        # Handle vehicle assignment (Sync from Driver Management)
        vehicle_id = request.data.get('vehicle_id')
        if 'vehicle_id' in request.data:
            from vehicles.models import Vehicle
            if vehicle_id:
                try:
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                    user.vehicle = vehicle
                except Vehicle.DoesNotExist:
                    user.vehicle = None
            else:
                user.vehicle = None
            user.save()

        return Response({'message': 'User updated successfully'})

    elif request.method == 'DELETE':
        # Hard delete - Xóa vĩnh viễn khỏi CSDL
        try:
            from django.db import connection
            
            user_id = str(user.id)
            
            # Xóa user bằng raw SQL để bypass hoàn toàn Django admin log
            with connection.cursor() as cursor:
                # Gỡ liên kết xe trước (SET driver_id = NULL)
                cursor.execute("UPDATE vehicles SET driver_id = NULL WHERE driver_id = %s", [user_id])
                # Gỡ liên kết orders
                cursor.execute("UPDATE orders SET driver_id = NULL WHERE driver_id = %s", [user_id])
                # Gỡ liên kết routes
                cursor.execute("UPDATE routes SET driver_id = NULL WHERE driver_id = %s", [user_id])
                # Xóa các liên kết trong bảng user_groups và user_permissions
                cursor.execute("DELETE FROM users_groups WHERE user_id = %s", [user_id])
                cursor.execute("DELETE FROM users_user_permissions WHERE user_id = %s", [user_id])
                # Xóa user
                cursor.execute("DELETE FROM users WHERE id = %s", [user_id])
            
            return Response({'message': 'Đã xóa tài xế thành công'})
        except Exception as e:
            return Response({'error': f'Không thể xóa: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_delivery_failed(request):
    """Tài xế báo giao thất bại - Tạo transaction chờ Admin xác nhận"""
    from orders.models import Order
    from transactions.models import Transaction
    from transport.models import RouteStop, Route
    from django.utils import timezone
    
    order_id = request.data.get('order_id')
    reason = request.data.get('reason', '')
    
    if not order_id:
        return Response({'error': 'Order ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(pk=order_id, drivers=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update RouteStop status to skipped (để đơn tiếp theo nhảy lên)
    try:
        route_stop = RouteStop.objects.filter(order_id=order_id).first()
        if route_stop:
            route_stop.status = 'skipped'
            route_stop.save()
    except Exception as e:
        print(f"Error updating RouteStop: {e}")
    
    # Đổi trạng thái đơn hàng sang 'failed' để không hiện ở tài xế nữa
    order.status = 'failed'
    order.save()
    
    # KHÔNG auto-complete route ở đây - chờ admin xác nhận ở Lịch sử giao dịch
    
    # Tạo transaction ghi nhận giao thất bại - CHƯA cộng thể tích
    # Admin sẽ xác nhận sau -> lúc đó mới cộng lại thể tích và hoàn thành route
    Transaction.objects.create(
        order_id=order.id,
        order_code=order.order_code,
        driver_id=request.user.id,
        driver_name=request.user.full_name or request.user.username,
        completed_at=timezone.now(),
        location=order.delivery_address,
        status='failed_pending',  # Trạng thái chờ admin xác nhận thất bại
        notes=f'Lý do: {reason}' if reason else 'Giao thất bại - chờ xác nhận',
    )
    
    return Response({
        'message': 'Đã gửi báo cáo thất bại - Chờ Admin xác nhận',
        'reason': reason
    })



