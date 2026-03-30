"""
Bin Packing Algorithm for Vehicle Loading
Uses First Fit Decreasing (FFD) algorithm to optimally assign orders to vehicles
"""


def first_fit_decreasing(orders, vehicles):
    """
    First Fit Decreasing (FFD) bin packing algorithm
    
    Args:
        orders: list of dicts with 'id', 'weight', 'volume' (optional)
        vehicles: list of dicts with 'id', 'capacity_kg', 'capacity_volume' (optional)
    
    Returns:
        dict with vehicle assignments
    """
    # Normalize all numeric fields to float/int to avoid Decimal type errors
    for o in orders:
        o['weight'] = float(o.get('weight', 1) or 1)
        o['volume'] = float(o.get('volume', 0.01) or 0.01)
    for v in vehicles:
        v['capacity_kg'] = int(v.get('capacity_kg', 1000) or 1000)
        v['capacity_volume'] = float(v.get('capacity_volume', 100) or 100)

    # Sort orders by weight (descending) - largest first
    sorted_orders = sorted(orders, key=lambda x: x.get('weight', 0), reverse=True)
    
    # Initialize vehicle bins
    bins = []
    for v in vehicles:
        bins.append({
            'vehicle_id': v['id'],
            'vehicle_plate': v.get('plate', ''),
            'capacity_kg': v.get('capacity_kg', 1000),
            'capacity_volume': v.get('capacity_volume', 100),
            'current_weight': 0,
            'current_volume': 0,
            'orders': [],
        })
    
    unassigned = []
    
    # FFD: Try to fit each order into first available vehicle
    for order in sorted_orders:
        order_weight = order.get('weight', 1)
        order_volume = order.get('volume', 0.1)
        placed = False
        
        for bin in bins:
            remaining_weight = bin['capacity_kg'] - bin['current_weight']
            remaining_volume = bin['capacity_volume'] - bin['current_volume']
            
            if order_weight <= remaining_weight and order_volume <= remaining_volume:
                # Fits! Add to this vehicle
                bin['orders'].append({
                    'order_id': order['id'],
                    'order_code': order.get('code', ''),
                    'weight': order_weight,
                    'volume': order_volume,
                })
                bin['current_weight'] += order_weight
                bin['current_volume'] += order_volume
                placed = True
                break
        
        if not placed:
            unassigned.append(order)
    
    # Calculate stats
    result = {
        'assignments': [],
        'unassigned': unassigned,
        'summary': {
            'total_orders': len(orders),
            'assigned_orders': len(orders) - len(unassigned),
            'unassigned_orders': len(unassigned),
            'vehicles_used': 0,
        }
    }
    
    for bin in bins:
        if bin['orders']:
            result['summary']['vehicles_used'] += 1
            weight_pct = round((bin['current_weight'] / bin['capacity_kg']) * 100, 1) if bin['capacity_kg'] > 0 else 0
            volume_pct = round((bin['current_volume'] / bin['capacity_volume']) * 100, 1) if bin['capacity_volume'] > 0 else 0
            
            result['assignments'].append({
                'vehicle_id': bin['vehicle_id'],
                'vehicle_plate': bin['vehicle_plate'],
                'orders': bin['orders'],
                'total_weight': bin['current_weight'],
                'total_volume': round(bin['current_volume'], 2),
                'weight_utilization_pct': weight_pct,
                'volume_utilization_pct': volume_pct,
                'remaining_capacity_kg': bin['capacity_kg'] - bin['current_weight'],
            })
    
    return result


def best_fit_decreasing(orders, vehicles):
    """
    Best Fit Decreasing variant - assigns to vehicle with least remaining space
    that can still fit the order (tighter packing)
    """
    sorted_orders = sorted(orders, key=lambda x: x.get('weight', 0), reverse=True)
    
    bins = []
    for v in vehicles:
        bins.append({
            'vehicle_id': v['id'],
            'vehicle_plate': v.get('plate', ''),
            'capacity_kg': v.get('capacity_kg', 1000),
            'current_weight': 0,
            'orders': [],
        })
    
    unassigned = []
    
    for order in sorted_orders:
        order_weight = order.get('weight', 1)
        
        # Find best fit: vehicle with minimum remaining space that can still fit
        best_bin = None
        best_remaining = float('inf')
        
        for bin in bins:
            remaining = bin['capacity_kg'] - bin['current_weight']
            if order_weight <= remaining < best_remaining:
                best_bin = bin
                best_remaining = remaining
        
        if best_bin:
            best_bin['orders'].append({
                'order_id': order['id'],
                'order_code': order.get('code', ''),
                'weight': order_weight,
            })
            best_bin['current_weight'] += order_weight
        else:
            unassigned.append(order)
    
    # Build result
    result = {
        'assignments': [],
        'unassigned': unassigned,
        'summary': {
            'total_orders': len(orders),
            'assigned_orders': len(orders) - len(unassigned),
            'unassigned_orders': len(unassigned),
            'vehicles_used': 0,
        }
    }
    
    for bin in bins:
        if bin['orders']:
            result['summary']['vehicles_used'] += 1
            result['assignments'].append({
                'vehicle_id': bin['vehicle_id'],
                'vehicle_plate': bin['vehicle_plate'],
                'orders': bin['orders'],
                'total_weight': bin['current_weight'],
                'weight_utilization_pct': round((bin['current_weight'] / bin['capacity_kg']) * 100, 1),
            })
    
    return result
