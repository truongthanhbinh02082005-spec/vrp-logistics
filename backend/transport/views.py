from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Route, RouteStop
from orders.models import Order
from vehicles.models import Vehicle
import math


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def route_list(request):
    if request.method == 'GET':
        status_filter = request.query_params.get('status')
        routes = Route.objects.all()

        if status_filter:
            routes = routes.filter(status=status_filter)

        from vehicles.models import Vehicle
        from authentication.models import User
        vehicles_dict = {str(v.id): v for v in Vehicle.objects.all()}
        users = {str(u.id): u.full_name or u.username for u in User.objects.all()}
        
        # Pre-fetch orders to calculate route payload without N+1
        from orders.models import Order
        order_ids = set()
        for r in routes:
            for stop in r.stops.all():
                if stop.order_id:
                    order_ids.add(stop.order_id)
                    
        orders_data = Order.objects.filter(id__in=order_ids).values('id', 'weight', 'volume', 'amount', 'order_code')
        order_lookup = {str(o['id']): o for o in orders_data}

        data = []
        for r in routes:
            vehicle = vehicles_dict.get(str(r.vehicle_id)) if r.vehicle_id else None
            
            # Calculate current payload
            r_weight = 0
            r_volume = 0
            stops = r.stops.all().order_by('sequence')
            stops_data = []
            for s in stops:
                if s.order_id:
                    o_data = order_lookup.get(str(s.order_id))
                    if o_data:
                        w_val = float(o_data.get('weight', 0) or o_data.get('amount', 0)/100 or 1.0)
                        v_val = float(o_data.get('volume', 0.01) or 0.01)
                        r_weight += max(1.0, w_val)
                        r_volume += v_val
                        
                stops_data.append({
                    'id': str(s.id),
                    'sequence': s.sequence,
                    'latitude': float(s.latitude) if s.latitude else None,
                    'longitude': float(s.longitude) if s.longitude else None,
                    'order_id': str(s.order_id) if s.order_id else None,
                    'order_code': order_lookup.get(str(s.order_id), {}).get('order_code') if s.order_id else None,
                    'address': s.address,
                    'stop_type': s.stop_type,
                })
                
            data.append({
                'id': str(r.id),
                'code': r.code,
                'vehicle_id': str(r.vehicle_id) if r.vehicle_id else None,
                'vehicle_plate': vehicle.code if vehicle else None,
                'drivers': [{'id': str(d.id), 'name': d.full_name or d.username} for d in r.drivers.all()],
                'status': r.status,
                'total_distance': float(r.total_distance) if r.total_distance else 0,
                'total_time': r.total_time,
                'total_orders': r.total_orders,
                'start_time': r.start_time.isoformat() if r.start_time else None,
                'end_time': r.end_time.isoformat() if r.end_time else None,
                'created_at': r.created_at.isoformat() if r.created_at else None,
                'total_weight': round(r_weight, 2),
                'total_volume': round(r_volume, 2),
                'capacity_kg': vehicle.capacity_kg if vehicle and vehicle.capacity_kg > 0 else 1000,
                'capacity_volume': float(vehicle.capacity_volume) if vehicle and vehicle.capacity_volume else 100.0,
                'stops': stops_data
            })
            
        return Response(data)

    elif request.method == 'POST':
        count = Route.objects.count() + 1
        code = request.data.get('code', f"RT{timezone.now().strftime('%Y%m%d')}{count:04d}")

        route = Route.objects.create(
            code=code,
            vehicle_id=request.data.get('vehicle_id'),
            warehouse_id=request.data.get('warehouse_id'),
            status='pending',
        )
        driver_id = request.data.get('driver_id')
        if driver_id:
            route.drivers.add(driver_id)
        
        return Response({
            'id': str(route.id),
            'code': route.code,
            'message': 'Route created successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def route_detail(request, pk):
    try:
        route = Route.objects.get(pk=pk)
    except Route.DoesNotExist:
        return Response({'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        from vehicles.models import Vehicle
        from authentication.models import User
        
        vehicle_plate = None
        driver_name = None
        
        if route.vehicle_id:
            try:
                vehicle = Vehicle.objects.get(id=route.vehicle_id)
                vehicle_plate = vehicle.code
            except Vehicle.DoesNotExist:
                pass
                
        if route.driver_id:
            try:
                driver = User.objects.get(id=route.driver_id)
                driver_name = driver.full_name or driver.username
            except User.DoesNotExist:
                pass

        stops = RouteStop.objects.filter(route=route).order_by('sequence')
        stops_data = [{
            'id': str(s.id),
            'sequence': s.sequence,
            'order_id': str(s.order_id) if s.order_id else None,
            'order_code': Order.objects.get(pk=s.order_id).order_code if s.order_id else None,
            'warehouse_id': str(s.warehouse_id) if s.warehouse_id else None,
            'stop_type': s.stop_type,
            'address': s.address,
            'latitude': float(s.latitude) if s.latitude else None,
            'longitude': float(s.longitude) if s.longitude else None,
            'status': s.status,
            'planned_arrival': s.planned_arrival.isoformat() if s.planned_arrival else None,
            'actual_arrival': s.actual_arrival.isoformat() if s.actual_arrival else None,
            'distance_from_previous': float(s.distance_from_previous) if s.distance_from_previous else 0,
            'time_from_previous': s.time_from_previous,
        } for s in stops]

        drivers_data = [{
            'id': str(d.id),
            'username': d.username,
            'full_name': d.full_name
        } for d in route.drivers.all()]

        return Response({
            'id': str(route.id),
            'code': route.code,
            'vehicle_id': str(route.vehicle_id) if route.vehicle_id else None,
            'vehicle_plate': vehicle_plate,
            'drivers': drivers_data,
            'warehouse_id': str(route.warehouse_id) if route.warehouse_id else None,
            'status': route.status,
            'total_distance': float(route.total_distance) if route.total_distance else 0,
            'total_time': route.total_time,
            'total_orders': route.total_orders,
            'stops': stops_data,
        })

    elif request.method == 'PUT':
        route.status = request.data.get('status', route.status)
        route.vehicle_id = request.data.get('vehicle_id', route.vehicle_id)
        route.driver_id = request.data.get('driver_id', route.driver_id)
        route.notes = request.data.get('notes', route.notes)
        route.save()
        return Response({'message': 'Route updated successfully'})

    elif request.method == 'DELETE':
        route.delete()
        return Response({'message': 'Route deleted successfully'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_routes(request):
    """Xóa tất cả lộ trình (kể cả đã giao) và đặt lại hệ thống (đưa đơn hàng về pending, xóa giao dịch)"""
    try:
        from vehicles.models import Vehicle
        from transactions.models import Transaction
        
        routes = Route.objects.exclude(status='cancelled')
        
        # Giải phóng tất cả xe đang bận
        Vehicle.objects.update(status='available')
        
        # Collect order ids tied to these routes
        order_ids = RouteStop.objects.filter(route__in=routes).values_list('order_id', flat=True)
        
        # Đưa các đơn hàng này về trạng thái chờ
        Order.objects.filter(id__in=order_ids).update(
            status='pending',
            vehicle_id=None,
        )
        # Clear ManyToMany drivers for orders
        for o in Order.objects.filter(id__in=order_ids):
            o.drivers.clear()
        
        # Xóa tất cả các Giao dịch (Transactions) để reset sạch cho lần chạy map mới
        Transaction.objects.all().delete()
        
        count, _ = routes.delete()
        return Response({'message': f'Đã xóa {count} lộ trình, xóa giao dịch và đưa đơn hàng về chờ.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_route(request, pk):
    try:
        route = Route.objects.get(pk=pk)
    except Route.DoesNotExist:
        return Response({'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)

    route.status = 'in_progress'
    route.actual_start_time = timezone.now()
    route.save()

    # Update vehicle status
    if route.vehicle_id:
        try:
            vehicle = Vehicle.objects.get(pk=route.vehicle_id)
            vehicle.status = 'busy'
            vehicle.save()
        except Vehicle.DoesNotExist:
            pass

    return Response({'message': 'Route started successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_route(request, pk):
    try:
        route = Route.objects.get(pk=pk)
    except Route.DoesNotExist:
        return Response({'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)

    route.status = 'completed'
    route.actual_end_time = timezone.now()
    route.save()

    # Update vehicle status
    if route.vehicle_id:
        try:
            vehicle = Vehicle.objects.get(pk=route.vehicle_id)
            vehicle.status = 'available'
            vehicle.save()
        except Vehicle.DoesNotExist:
            pass

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_routes(request):
    """
    API tối ưu lộ trình VRP sử dụng OR-Tools
    Flow: 
      1. Nhận order_ids -> Tự lấy tất cả xe available có driver
      2. Bin Packing (FFD) -> Chia đơn hàng vào các xe theo tải trọng
      3. OR-Tools VRP -> Tối ưu thứ tự giao trong từng xe
    """
    from .vrp_solver import solve_vrp
    from warehouses.models import Warehouse
    from vehicles.bin_packing import first_fit_decreasing
    from authentication.models import User
    import traceback
    from django.utils import timezone

    try:
        order_ids = request.data.get('order_ids', [])
        driver_ids = request.data.get('driver_ids', [])

        if not order_ids:
            return Response({'error': 'No orders provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Lấy orders đang pending
        orders = Order.objects.filter(id__in=order_ids, status='pending')
        if not orders.exists():
            return Response({'error': 'Không có đơn hàng pending nào được chọn.'}, status=status.HTTP_400_BAD_REQUEST)

        # Unified: Tính tổng khối lượng đơn hàng (tránh con số 3000kg ảo)
        total_order_weight = sum(max(1.0, float(getattr(o, 'weight', 0) or 1.0)) for o in orders)

        # ==============================================
        # BƯỚC 1: Lấy xe rảnh
        # ==============================================
        busy_vehicle_ids = list(Route.objects.filter(
            status__in=['pending', 'in_progress']
        ).values_list('vehicle_id', flat=True))

        vehicles_qs = Vehicle.objects.exclude(id__in=busy_vehicle_ids)

        if not vehicles_qs.exists():
            return Response({'error': 'Tất cả các xe đang bận hoặc chưa có xe nào trong hệ thống.'}, status=status.HTTP_400_BAD_REQUEST)

        # Lọc drivers
        selected_drivers = list(User.objects.filter(id__in=driver_ids)) if driver_ids else []
        if not selected_drivers:
            return Response({'error': 'Vui lòng chọn ít nhất một tài xế rảnh.'}, status=status.HTTP_400_BAD_REQUEST)

        if driver_ids:
            busy_users = User.objects.filter(
                id__in=driver_ids, 
                routes__status__in=['pending', 'in_progress']
            ).distinct()
            if busy_users.exists():
                busy_names = [u.full_name or u.username for u in busy_users]
                return Response({'error': f"Tài xế {', '.join(busy_names)} đang thực hiện lộ trình chưa hoàn tất."}, status=status.HTTP_400_BAD_REQUEST)

        # THUẬT TOÁN: Chọn mỗi tài xế 1 xe (1 driver = 1 vehicle)
        available_vehicles = list(vehicles_qs)[:len(selected_drivers)]
        total_capacity = sum(v.capacity_kg if v.capacity_kg > 0 else 1000 for v in available_vehicles)

        if total_order_weight > total_capacity:
            return Response({
                'error': f"Tổng khối lượng hàng ({total_order_weight}kg) vượt quá tải trọng của {len(selected_drivers)} tài xế đã chọn ({total_capacity}kg).Vui lòng chọn thêm tài xế chưa có lộ trình."
            }, status=status.HTTP_400_BAD_REQUEST)

        from collections import defaultdict
        orders_by_warehouse = defaultdict(list)
        for o in orders:
            wh_id = str(o.warehouse_id) if getattr(o, 'warehouse_id', None) else 'unknown'
            orders_by_warehouse[wh_id].append(o)

        created_routes = []
        total_distance = 0
        total_original_distance = 0
        all_packing_summary = {
            'total_orders': len(orders),
            'assigned_orders': 0,
            'unassigned_orders': 0,
            'vehicles_used': 0
        }
        
        warehouse_info = {}
        for w_id in orders_by_warehouse.keys():
            if w_id != 'unknown':
                try:
                    wh = Warehouse.objects.get(pk=w_id)
                    if wh.lat and wh.lng:
                        warehouse_info[w_id] = {'lat': float(wh.lat), 'lng': float(wh.lng), 'name': wh.name}
                except Warehouse.DoesNotExist:
                    pass

        driver_index = 0
        for w_id, wh_orders in orders_by_warehouse.items():
            if not wh_orders or not available_vehicles:
                if not available_vehicles:
                    all_packing_summary['unassigned_orders'] += len(wh_orders)
                continue

            depot_location = {'lat': 10.8231, 'lng': 106.6297}
            if w_id in warehouse_info:
                depot_location = warehouse_info[w_id]

            orders_with_coords = []
            orders_data_for_packing = []
            for order in wh_orders:
                # Unified: Chỉ dùng trọng lượng thực
                weight_val = max(1.0, float(getattr(order, 'weight', 0) or 1.0))
                final_volume = float(getattr(order, 'volume', 0.01) or 0.01)
                orders_data_for_packing.append({
                    'id': str(order.id),
                    'code': order.order_code,
                    'weight': weight_val,
                    'volume': final_volume,
                })
                if order.delivery_lat and order.delivery_lng:
                    orders_with_coords.append({
                        'id': str(order.id),
                        'lat': float(order.delivery_lat),
                        'lng': float(order.delivery_lng),
                        'weight': weight_val,
                    })

            vehicles_data_for_packing = [{
                'id': str(v.id),
                'plate': v.code,
                'capacity_kg': v.capacity_kg if v.capacity_kg > 0 else 1000,
                'capacity_volume': float(v.capacity_volume) if v.capacity_volume else 100,
            } for v in available_vehicles]

            packing_result = first_fit_decreasing(orders_data_for_packing, vehicles_data_for_packing)
            all_packing_summary['assigned_orders'] += packing_result['summary']['assigned_orders']
            all_packing_summary['unassigned_orders'] += packing_result['summary']['unassigned_orders']
            all_packing_summary['vehicles_used'] += packing_result['summary']['vehicles_used']

            vehicle_order_map = {}
            for assignment in packing_result['assignments']:
                v_id_assigned = assignment['vehicle_id']
                vehicle_order_map[v_id_assigned] = [o['order_id'] for o in assignment['orders']]

            for vehicle in list(available_vehicles):
                v_id_str = str(vehicle.id)
                assigned_order_ids = vehicle_order_map.get(v_id_str, [])
                if not assigned_order_ids:
                    continue

                vehicle_order_locations = [o for o in orders_with_coords if o['id'] in assigned_order_ids]
                vehicle_demands = [int(max(1, o['weight'])) for o in vehicle_order_locations]
                if not vehicle_order_locations:
                    continue

                vehicle_capacity = vehicle.capacity_kg if vehicle.capacity_kg > 0 else 1000
                total_weight = sum(o['weight'] for o in vehicle_order_locations)

                try:
                    vrp_result = solve_vrp(
                        depot_location={'lat': depot_location['lat'], 'lng': depot_location['lng']},
                        order_locations=vehicle_order_locations,
                        vehicle_capacities=[vehicle_capacity],
                        order_demands=vehicle_demands
                    )
                except Exception as e:
                    print(f"VRP Error: {e}")
                    continue

                if not vrp_result.get('routes') or not vrp_result['routes'][0].get('stops'):
                    continue

                route_data = vrp_result['routes'][0]
                stops = route_data['stops']
                dist_km = route_data.get('distance_km', 0)
                total_distance += dist_km

                # Original distance (naive sequence)
                original_dist_km = 0
                if vehicle_order_locations:
                    from .vrp_solver import haversine_distance
                    original_dist_km += haversine_distance(depot_location['lat'], depot_location['lng'], vehicle_order_locations[0]['lat'], vehicle_order_locations[0]['lng'])
                    for i in range(len(vehicle_order_locations)-1):
                        original_dist_km += haversine_distance(vehicle_order_locations[i]['lat'], vehicle_order_locations[i]['lng'], vehicle_order_locations[i+1]['lat'], vehicle_order_locations[i+1]['lng'])
                    original_dist_km += haversine_distance(vehicle_order_locations[-1]['lat'], vehicle_order_locations[-1]['lng'], depot_location['lat'], depot_location['lng'])
                total_original_distance += original_dist_km

                import uuid
                from datetime import timedelta
                unique_suffix = uuid.uuid4().hex[:6].upper()
                route = Route.objects.create(
                    code=f"RT{timezone.now().strftime('%Y%m%d')}{unique_suffix}",
                    vehicle_id=vehicle.id,
                    warehouse_id=w_id if w_id != 'unknown' else None,
                    status='pending',
                    total_orders=len(stops),
                    original_distance=original_dist_km,
                    total_distance=dist_km,
                    total_weight=total_weight
                )

                route_driver_names = []
                assigned_driver = None
                if selected_drivers:
                    assigned_driver = selected_drivers[driver_index % len(selected_drivers)]
                    route.drivers.set([assigned_driver])
                    route_driver_names = [assigned_driver.full_name or assigned_driver.username]
                    driver_index += 1

                current_time = timezone.now()
                for stop in stops:
                    try:
                        o = Order.objects.get(pk=stop['order_id'])
                        o.vehicle_id = vehicle.id
                        if assigned_driver: o.drivers.set([assigned_driver])
                        o.status = 'assigned'
                        o.save()
                        RouteStop.objects.create(
                            route=route,
                            order_id=o.id,
                            sequence=stop['sequence'],
                            stop_type='delivery',
                            address=o.delivery_address,
                            latitude=o.delivery_lat,
                            longitude=o.delivery_lng,
                            status='pending',
                            planned_arrival=current_time + timedelta(minutes=30 * stop['sequence']),
                        )
                    except: continue

                available_vehicles = [v for v in available_vehicles if str(v.id) != v_id_str]
                created_routes.append({
                    'id': str(route.id),
                    'code': route.code,
                    'vehicle_plate': vehicle.code,
                    'drivers': route_driver_names,
                    'orders_count': len(stops),
                    'distance_km': dist_km,
                    'total_weight': round(total_weight, 1),
                    'capacity_kg': vehicle_capacity
                })

        if not created_routes:
            return Response({'error': 'Không tạo được lộ trình nào. Các xe hiện tại không đủ khoảng trống hoặc lỗi VRP.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'Tối ưu hoàn tất!',
            'algorithm': 'FFD Bin Packing + OR-Tools CVRP',
            'bin_packing_summary': {
                **all_packing_summary,
                'total_weight_kg': round(total_order_weight, 1),
                'total_capacity_kg': total_capacity
            },
            'total_distance_km': round(total_distance, 2),
            'original_distance_km': round(total_original_distance, 2),
            'routes': created_routes,
        })

    except Exception as e:
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_stop_status(request, route_pk, stop_pk):
    """Cập nhật trạng thái điểm dừng"""
    try:
        stop = RouteStop.objects.get(pk=stop_pk, route_id=route_pk)
    except RouteStop.DoesNotExist:
        return Response({'error': 'Stop not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status:
        stop.status = new_status
        if new_status == 'arrived':
            stop.actual_arrival = timezone.now()
        elif new_status == 'completed':
            stop.departure_time = timezone.now()
        stop.save()
        return Response({'message': 'Stop status updated successfully'})
    return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def distance_matrix_view(request):
    """
    Trả về ma trận khoảng cách (km) giữa kho và các đơn hàng.
    Input: { order_ids: [...] }
    Output: { labels: [...], matrix: [[...]] }
    """
    from .vrp_solver import haversine_distance
    from warehouses.models import Warehouse

    order_ids = request.data.get('order_ids', [])
    warehouse_id_param = request.data.get('warehouse_id')
    
    if not order_ids and warehouse_id_param:
        orders = Order.objects.filter(warehouse_id=warehouse_id_param).exclude(status='pending').exclude(status='cancelled')
        if not orders.exists():
            return Response({'matrices': [], 'is_multi': True, 'message': 'Không có đơn hàng đã tối ưu tại kho này.'}, status=status.HTTP_200_OK)
        warehouse_ids = [warehouse_id_param]
    else:
        orders = Order.objects.filter(id__in=order_ids)
        if not orders.exists():
            return Response({'error': 'No orders found'}, status=status.HTTP_400_BAD_REQUEST)
        # Lấy TẤT CẢ các kho liên quan đến các đơn hàng đươc chọn
        warehouse_ids = set([str(o.warehouse_id) for o in orders if getattr(o, 'warehouse_id', None)])
    
    if not warehouse_ids:
        return Response({'error': 'No warehouses identified'}, status=status.HTTP_400_BAD_REQUEST)

    results = []
    
    # Gom nhóm đơn theo từng kho để tạo các ma trận độc lập
    for w_id in warehouse_ids:
        try:
            warehouse = Warehouse.objects.get(pk=w_id)
            if not warehouse.lat or not warehouse.lng:
                continue
                
            # Tạo danh sách location bắt đầu bằng Kho này
            locations = [{
                'label': f'🏭 {warehouse.name}',
                'lat': float(warehouse.lat),
                'lng': float(warehouse.lng),
            }]
            
            # Chỉ lấy các đơn hàng thuộc kho này
            wh_orders = [o for o in orders if str(getattr(o, 'warehouse_id', '')) == str(w_id)]
            for order in wh_orders:
                if order.delivery_lat and order.delivery_lng:
                    locations.append({
                        'label': order.order_code,
                        'lat': float(order.delivery_lat),
                        'lng': float(order.delivery_lng),
                    })
                    
            if len(locations) < 2:
                continue # Nếu kho ko có đơn nào hợp lệ thì bỏ qua ko hiện ma trận
                
            n = len(locations)
            labels = [loc['label'] for loc in locations]
            matrix = []
            
            for i in range(n):
                row = []
                for j in range(n):
                    if i == j:
                        row.append(0.0)
                    else:
                        dist = haversine_distance(
                            locations[i]['lat'], locations[i]['lng'],
                            locations[j]['lat'], locations[j]['lng']
                        )
                        row.append(round(dist, 2))
                matrix.append(row)
                
            results.append({
                'warehouse_name': warehouse.name,
                'labels': labels,
                'matrix': matrix,
                'size': n,
            })
            
        except Warehouse.DoesNotExist:
            continue

    # API giờ trả về 1 mảng các ma trận ứng với các kho xuất phát
    return Response({
        'matrices': results,
        'is_multi': True,
        'message': 'No data available for this selection' if not results else 'Success'
    }, status=status.HTTP_200_OK)
