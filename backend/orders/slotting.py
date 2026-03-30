from .models import Order

# Cấu trúc kho hàng với sức chứa lớn
# Mỗi kệ: 20 Hàng (Rows) x 20 Cột (Cols) x 5 Tầng (Levels) = 2000 slots/kệ
# Tổng: 3 kệ x 2000 = 6000 slots/kho
WAREHOUSE_LAYOUT = {
    'A': {'rows': 20, 'cols': 20, 'levels': 5},
    'B': {'rows': 20, 'cols': 20, 'levels': 5},
    'C': {'rows': 20, 'cols': 20, 'levels': 5},
}

def get_warehouse_capacity():
    """Tính tổng sức chứa của kho"""
    total = 0
    for shelf, dims in WAREHOUSE_LAYOUT.items():
        total += dims['rows'] * dims['cols'] * dims['levels']
    return total

def auto_assign_slot(order_instance):
    """
    Tìm vị trí trống đầu tiên trong kho để gán cho đơn hàng.
    Lưu format: "SHELF-ROW-COL-LEVEL" (VD: "A-0-1-1")
    """
    # Lấy tất cả các vị trí đang bị chiếm TRONG KHO ĐÓ
    occupied_slots = set(
        Order.objects.filter(
            status__in=['pending', 'confirmed', 'assigned'],
            shelf_position__isnull=False,
            warehouse_id=order_instance.warehouse_id
        ).values_list('shelf_position', flat=True)
    )

    # Nếu chưa gán kho, không thể xếp slot
    if not order_instance.warehouse_id:
        print("⚠️ Order has no Warehouse ID. Cannot assign slot.")
        return None

    # Duyệt qua từng vị trí trong kho để tìm chỗ trống
    for shelf_name, dims in WAREHOUSE_LAYOUT.items():
        for r in range(dims['rows']):
            for c in range(dims['cols']):
                for l in range(dims['levels']):
                    position_code = f"{shelf_name}-{r}-{c}-{l}"
                    
                    if position_code not in occupied_slots:
                        # Found empty slot!
                        order_instance.shelf_position = position_code
                        order_instance.save()
                        print(f"✅ Assigned Order {order_instance.order_code} to slot {position_code}")
                        return position_code
    
    print(f"⚠️ Warehouse FULL! Cannot assign slot for {order_instance.order_code}")
    return None
