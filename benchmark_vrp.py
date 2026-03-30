import sys
import os
import time
import random
import json

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from transport.vrp_solver import solve_vrp, haversine_distance
from benchmark.vrp_parser import parse_vrp_file

def calculate_naive_distance(locations):
    """Simple sequential distance (1->2->3...->n->1)"""
    if len(locations) < 2:
        return 0
    total = 0
    # locations[0] is depot
    # Sequential: 0 -> 1 -> 2 ... -> n-1 -> 0
    for i in range(len(locations) - 1):
        total += haversine_distance(
            locations[i]['lat'], locations[i]['lng'],
            locations[i+1]['lat'], locations[i+1]['lng']
        )
    total += haversine_distance(
        locations[-1]['lat'], locations[-1]['lng'],
        locations[0]['lat'], locations[0]['lng']
    )
    return total

def run_benchmark(name, depot, orders, capacities):
    print(f"\n--- Running Benchmark: {name} ---")
    
    # Extract demands
    demands = [int(o.get('weight', 1)) for o in orders]
    
    start_time = time.time()
    
    # Run OR-Tools
    result = solve_vrp(depot, orders, capacities, order_demands=demands)
    
    end_time = time.time()
    latency = (end_time - start_time) * 1000 # ms
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return None
    
    # Calculate Naive Distance for comparison
    naive_dist = calculate_naive_distance([depot] + orders)
    opt_dist = result.get('total_distance_km', 0)
    
    improvement = ((naive_dist - opt_dist) / naive_dist * 100) if naive_dist > 0 else 0
    
    # Extra check if opt_dist is 0 but routes exist
    if opt_dist == 0 and result.get('routes'):
         # Sum distance_km from routes
         opt_dist = sum(r.get('distance_km', 0) for r in result['routes'])
         improvement = ((naive_dist - opt_dist) / naive_dist * 100) if naive_dist > 0 else 0

    num_v = result.get('num_vehicles_used', len([r for r in result.get('routes', []) if r]))
    
    print(f"Nodes: {len(orders) + 1}")
    print(f"Vehicles Used: {num_v}")
    print(f"Original Distance: {naive_dist:.2f} km")
    print(f"Optimized Distance: {opt_dist:.2f} km")
    print(f"Improvement: {improvement:.2f}%")
    print(f"Latency: {latency:.2f} ms")
    
    return {
        'name': name,
        'nodes': len(orders) + 1,
        'vehicles': num_v,
        'original_dist': naive_dist,
        'optimized_dist': opt_dist,
        'improvement': improvement,
        'latency': latency
    }

def generate_random_orders(count):
    # Center around Can Tho (10.0333, 105.7833)
    orders = []
    for i in range(count):
        orders.append({
            'id': f"ORD-{i}",
            'lat': 10.0333 + random.uniform(-0.05, 0.05),
            'lng': 105.7833 + random.uniform(-0.05, 0.05),
            'weight': random.randint(10, 50)
        })
    return orders

def main():
    results = []
    
    # 1. Benchmark A-n32-k5 (Using Haversine for mock GPS coords)
    vrp_32_path = os.path.join('backend', 'A', 'A', 'A-n32-k5.vrp')
    if os.path.exists(vrp_32_path):
        data = parse_vrp_file(vrp_32_path)
        # Mocking GPS coords from X,Y (rough scaling)
        depot = {'lat': 10.0 + data['nodes'][data['depot_id']]['y']/1000, 'lng': 105.0 + data['nodes'][data['depot_id']]['x']/1000}
        orders = []
        for nid, node in data['nodes'].items():
            if nid != data['depot_id']:
                orders.append({
                    'id': nid,
                    'lat': 10.0 + node['y']/1000,
                    'lng': 105.0 + node['x']/1000,
                    'weight': data['demands'].get(nid, 1)
                })
        capacities = [data['capacity']] * 5
        results.append(run_benchmark("A-n32-k5", depot, orders, capacities))

    # 2. Benchmark A-n33-k5
    vrp_33_path = os.path.join('backend', 'A', 'A', 'A-n33-k5.vrp')
    if os.path.exists(vrp_33_path):
        data = parse_vrp_file(vrp_33_path)
        depot = {'lat': 10.0 + data['nodes'][data['depot_id']]['y']/1000, 'lng': 105.0 + data['nodes'][data['depot_id']]['x']/1000}
        orders = []
        for nid, node in data['nodes'].items():
            if nid != data['depot_id']:
                orders.append({
                    'id': nid,
                    'lat': 10.0 + node['y']/1000,
                    'lng': 105.0 + node['x']/1000,
                    'weight': data['demands'].get(nid, 1)
                })
        capacities = [data['capacity']] * 5
        results.append(run_benchmark("A-n33-k5", depot, orders, capacities))

    # 3. Real-world 200 orders (Synthetic)
    depot_200 = {'lat': 10.0333, 'lng': 105.7833}
    orders_200 = generate_random_orders(200)
    capacities_200 = [500] * 36 # Based on user's 36 vehicles
    results.append(run_benchmark("Real-200 Orders", depot_200, orders_200, capacities_200))

    # Save summary for report
    print("\n" + "="*50)
    print(f"{'Instance':<20} | {'Nodes':<5} | {'Original (km)':<15} | {'Optimized (km)':<15} | {'Saved (%)':<10} | {'Latency (ms)':<10}")
    print("-" * 95)
    for r in results:
        if r:
            print(f"{r['name']:<20} | {r['nodes']:<5} | {r['original_dist']:<15.2f} | {r['optimized_dist']:<15.2f} | {r['improvement']:<10.2f} | {r['latency']:<10.2f}")

    # Write to file
    with open('benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
