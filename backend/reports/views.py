from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from vehicles.models import Vehicle
from warehouses.models import Warehouse
from transport.models import Route, RouteStop


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """API thống kê tổng quan cho Dashboard"""
    try:
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        in_transit_orders = Order.objects.filter(status='in_transit').count()
        completed_orders = Order.objects.filter(status='delivered').count()

        total_vehicles = Vehicle.objects.count()
        available_vehicles = Vehicle.objects.filter(status='available').count()
        busy_vehicles = Vehicle.objects.filter(status='busy').count()

        total_warehouses = Warehouse.objects.count()
        # Warehouse không có cột status trong database, mặc định tất cả active
        active_warehouses = total_warehouses

        total_routes = Route.objects.count()
        active_routes = Route.objects.filter(status='in_progress').count()
        completed_routes = Route.objects.filter(status='completed').count()

        # Today stats
        today = timezone.now().date()
        orders_today = Order.objects.filter(created_at__date=today).count()
        # Order không có cột delivered_at, mặc định 0
        delivered_today = 0

        return Response({
            'orders': {
                'total': total_orders,
                'pending': pending_orders,
                'in_transit': in_transit_orders,
                'completed': completed_orders,
                'today': orders_today,
                'delivered_today': delivered_today,
            },
            'vehicles': {
                'total': total_vehicles,
                'available': available_vehicles,
                'busy': busy_vehicles,
            },
            'warehouses': {
                'total': total_warehouses,
                'active': active_warehouses,
            },
            'routes': {
                'total': total_routes,
                'active': active_routes,
                'completed': completed_routes,
            }
        })
    except Exception as e:
        return Response({
            'orders': {'total': 0, 'pending': 0, 'in_transit': 0, 'completed': 0, 'today': 0, 'delivered_today': 0},
            'vehicles': {'total': 0, 'available': 0, 'busy': 0},
            'warehouses': {'total': 0, 'active': 0},
            'routes': {'total': 0, 'active': 0, 'completed': 0}
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_report(request):
    """Báo cáo đơn hàng theo trạng thái"""
    try:
        status_counts = Order.objects.values('status').annotate(count=Count('id'))
        
        # Orders by date (last 7 days)
        orders_by_date = []
        for i in range(7):
            date = (timezone.now() - timedelta(days=6-i)).date()
            count = Order.objects.filter(created_at__date=date).count()
            orders_by_date.append({'date': str(date), 'count': count})

        return Response({
            'status_breakdown': list(status_counts),
            'orders_by_date': orders_by_date,
        })
    except Exception as e:
        return Response({
            'status_breakdown': [],
            'orders_by_date': [],
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vehicle_report(request):
    """Báo cáo phương tiện"""
    try:
        status_counts = Vehicle.objects.values('status').annotate(count=Count('id'))
        type_counts = Vehicle.objects.values('vehicle_type').annotate(count=Count('id'))
        
        total_capacity = Vehicle.objects.aggregate(total=Sum('capacity_kg'))['total'] or 0
        average_capacity = Vehicle.objects.aggregate(avg=Avg('capacity_kg'))['avg'] or 0

        return Response({
            'status_breakdown': list(status_counts),
            'type_breakdown': list(type_counts),
            'total_capacity': float(total_capacity),
            'average_capacity': float(average_capacity),
        })
    except Exception as e:
        return Response({
            'status_breakdown': [],
            'type_breakdown': [],
            'total_capacity': 0,
            'average_capacity': 0,
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def route_report(request):
    """Báo cáo lộ trình & Hiệu suất VRP"""
    try:
        status_counts = Route.objects.values('status').annotate(count=Count('id'))

        # Last 7 days routes
        week_ago = timezone.now() - timedelta(days=7)
        routes_this_week = Route.objects.filter(created_at__gte=week_ago).count()
        
        active_routes = Route.objects.exclude(status='cancelled')
        
        # 1. Quãng đường bản đồ cung cấp (original_distance)
        total_original_distance = active_routes.aggregate(total=Sum('original_distance'))['total'] or 0
        
        # 2. Quãng đường thuật toán tối ưu (total_distance)
        total_optimized_distance = active_routes.aggregate(total=Sum('total_distance'))['total'] or 0
        
        # 3. Khối lượng tất cả đơn hàng (trên các chuyến xe này)
        order_ids_on_routes = RouteStop.objects.filter(route__in=active_routes).exclude(order_id__isnull=True).values_list('order_id', flat=True)
        total_delivered_weight = Order.objects.filter(id__in=order_ids_on_routes).aggregate(total=Sum('weight'))['total'] or 0
            
        # 4. Khối lượng tất cả xe đã sử dụng (Dựa trên capacity_kg của các xe được gán vào các Route chưa cancelled)
        total_used_capacity = 0
        for r in active_routes:
            if r.vehicle_id:
                try:
                    v = Vehicle.objects.get(pk=r.vehicle_id)
                    total_used_capacity += v.capacity_kg
                except Vehicle.DoesNotExist:
                    pass

        avg_distance = active_routes.aggregate(avg=Avg('total_distance'))['avg'] or 0
        avg_time = active_routes.aggregate(avg=Avg('total_time'))['avg'] or 0
        
        # Calculate estimated cost based on region/warehouse
        estimated_cost = 0
        
        for r in active_routes:
            dist = float(r.total_distance or 0)
            if not r.warehouse_id:
                estimated_cost += dist * 6000  # Default HCM
                continue
                
            try:
                from warehouses.models import Warehouse
                wh = Warehouse.objects.get(pk=r.warehouse_id)
                name = wh.name.lower()
                if 'cần thơ' in name or 'can tho' in name:
                    estimated_cost += dist * 5000
                elif 'đà nẵng' in name or 'da nang' in name or 'hà nội' in name or 'ha noi' in name:
                    estimated_cost += dist * 7000
                else:
                    estimated_cost += dist * 6000
            except:
                estimated_cost += dist * 6000

        return Response({
            'status_breakdown': list(status_counts),
            'routes_this_week': routes_this_week,
            'total_original_distance_km': float(total_original_distance),
            'total_optimized_distance_km': float(total_optimized_distance),
            'total_delivered_weight_kg': float(total_delivered_weight),
            'total_used_vehicle_capacity_kg': float(total_used_capacity),
            'average_distance_km': float(avg_distance) if avg_distance else 0,
            'avg_time': float(avg_time),
            'estimated_cost_vnd': estimated_cost,
            'delivery_density': float(len(order_ids_on_routes) / total_optimized_distance) if total_optimized_distance > 0 else 0,
        })
    except Exception as e:
        import traceback
        print(f"Error in route_report: {e}")
        traceback.print_exc()
        return Response({
            'status_breakdown': [],
            'routes_this_week': 0,
            'total_original_distance_km': 0,
            'total_optimized_distance_km': 0,
            'total_delivered_weight_kg': 0,
            'total_used_vehicle_capacity_kg': 0,
            'average_distance_km': 0,
            'avg_time': 0,
            'estimated_cost_vnd': 0,
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def performance_report(request):
    """Báo cáo hiệu suất"""
    try:
        total_orders = Order.objects.count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        failed_orders = Order.objects.filter(status__in=['failed', 'cancelled']).count()
        
        finished_orders = delivered_orders + failed_orders
        delivery_success_rate = (delivered_orders / finished_orders * 100) if finished_orders > 0 else 0
        
        total_vehicles = Vehicle.objects.count()
        busy_vehicles = Vehicle.objects.filter(status='busy').count()
        vehicle_utilization_rate = (busy_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0
        
        # Average delivery time
        avg_delivery_time = Route.objects.filter(status='completed').aggregate(
            avg=Avg('total_time')
        )['avg'] or 0
        
        return Response({
            'delivery_success_rate': round(delivery_success_rate, 1),
            'total_deliveries': delivered_orders,
            'average_delivery_time_minutes': round(float(avg_delivery_time), 1),
            'vehicle_utilization_rate': round(vehicle_utilization_rate, 1),
        })
    except Exception as e:
        return Response({
            'delivery_success_rate': 0,
            'total_deliveries': 0,
            'average_delivery_time_minutes': 0,
            'vehicle_utilization_rate': 0,
        })


