import math
from warehouses.models import Warehouse
from django.db.models import F

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách giữa 2 điểm tọa độ (km)
    """
    if None in [lat1, lon1, lat2, lon2]:
        return float('inf')
        
    R = 6371  # Earth radius in km
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + \
        math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * \
        math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def assign_nearest_warehouse(order_instance):
    """
    Tìm kho gần nhất với địa chỉ giao hàng và gán cho đơn hàng.
    """
    if not order_instance.delivery_lat or not order_instance.delivery_lng:
        print("⚠️ Order missing coordinates, skipping auto-allocation.")
        return None

    warehouses = Warehouse.objects.all() # Có thể filter status='active'
    
    nearest_warehouse = None
    min_dist = float('inf')

    for wh in warehouses:
        if wh.lat and wh.lng:
            dist = haversine_distance(
                order_instance.delivery_lat, order_instance.delivery_lng,
                wh.lat, wh.lng
            )
            print(f"DEBUG: Distance to {wh.name}: {dist:.2f} km")
            
            # Simple logic: Just closest distance. 
            # Advanced: Check capacity logic here if needed (e.g. check slotting usage)
            if dist < min_dist:
                min_dist = dist
                nearest_warehouse = wh

    if nearest_warehouse:
        order_instance.warehouse_id = nearest_warehouse.id
        order_instance.save()
        print(f"✅ Assigned Order {order_instance.order_code} to Warehouse {nearest_warehouse.name} ({min_dist:.2f} km)")
        return nearest_warehouse
    else:
        print("⚠️ No suitable warehouse found.")
        return None
