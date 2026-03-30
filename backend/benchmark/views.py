"""
Benchmark API Views
Endpoints for running VRP algorithm on Augerat benchmark datasets.
"""
import os
import math
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import BenchmarkResult
import json

# Path to the A-series benchmark directory (now inside backend)
DATASET_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'A', 'A'))


def euc_2d_distance(n1, n2):
    dx = n1['x'] - n2['x']
    dy = n1['y'] - n2['y']
    return int(math.sqrt(dx * dx + dy * dy) + 0.5)


def compute_route_cost(route_node_ids, nodes, depot_id):
    if not route_node_ids:
        return 0
    depot = nodes[depot_id]
    total = 0
    prev = depot
    for nid in route_node_ids:
        curr = nodes[nid]
        total += euc_2d_distance(prev, curr)
        prev = curr
    total += euc_2d_distance(prev, depot)
    return total


def solve_instance_with_ortools(vrp_data, time_limit=15):
    """
    Run OR-Tools CVRP solver on a parsed VRP instance.
    Uses EUC_2D distances as per TSPLIB spec.
    Returns routes, total cost.
    """
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp

    nodes = vrp_data['nodes']
    demands = vrp_data['demands']
    depot_id = vrp_data['depot_id']
    capacity = vrp_data['capacity']
    num_trucks = vrp_data.get('num_trucks', 10)  # fallback to 10

    # Build location list: depot first, then customers
    depot_node = nodes[depot_id]
    customer_ids = sorted([nid for nid in nodes if nid != depot_id])

    # node_order[i] = original node id
    node_order = [depot_id] + customer_ids
    n = len(node_order)

    # Distance matrix
    dist_matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dist_matrix[i][j] = euc_2d_distance(nodes[node_order[i]], nodes[node_order[j]])

    # Demands list indexed same as node_order
    demand_list = [demands.get(nid, 0) for nid in node_order]

    manager = pywrapcp.RoutingIndexManager(n, num_trucks, 0)
    routing = pywrapcp.RoutingModel(manager)

    def dist_callback(from_idx, to_idx):
        return dist_matrix[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]

    transit_cb = routing.RegisterTransitCallback(dist_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_cb)

    def demand_callback(from_idx):
        return demand_list[manager.IndexToNode(from_idx)]

    demand_cb = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_cb, 0, [capacity] * num_trucks, True, 'Capacity'
    )

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_params.time_limit.seconds = time_limit

    solution = routing.SolveWithParameters(search_params)
    if not solution:
        return None, None

    routes = []
    total_cost = 0
    for v in range(num_trucks):
        route_nodes = []
        idx = routing.Start(v)
        while not routing.IsEnd(idx):
            node_idx = manager.IndexToNode(idx)
            if node_idx != 0:
                route_nodes.append(node_order[node_idx])
            idx = solution.Value(routing.NextVar(idx))
        if route_nodes:
            route_cost = compute_route_cost(route_nodes, nodes, depot_id)
            total_cost += route_cost
            routes.append({
                'nodes': route_nodes,
                'demand': sum(demands.get(n, 0) for n in route_nodes),
                'cost': route_cost,
            })

    return routes, total_cost


def compute_baseline_cost(nodes, demands, depot_id, capacity):
    """
    Baseline: Nearest Neighbor Heuristic (greedy, no optimization).
    """
    unvisited = set(nid for nid in nodes if nid != depot_id)
    depot = nodes[depot_id]
    routes = []
    total_cost = 0

    while unvisited:
        route = []
        route_demand = 0
        current = depot_id
        route_cost = 0

        while True:
            # Find nearest unvisited that fits in capacity
            best = None
            best_dist = float('inf')
            for nid in unvisited:
                d = demands.get(nid, 0)
                if route_demand + d <= capacity:
                    dist = euc_2d_distance(nodes[current], nodes[nid])
                    if dist < best_dist:
                        best_dist = dist
                        best = nid
            if best is None:
                break
            route.append(best)
            route_demand += demands.get(best, 0)
            route_cost += best_dist
            unvisited.remove(best)
            current = best

        # Return to depot
        route_cost += euc_2d_distance(nodes[current], depot)
        if route:
            routes.append({'nodes': route, 'demand': route_demand, 'cost': route_cost})
            total_cost += route_cost

    return routes, total_cost


@api_view(['GET'])
@permission_classes([AllowAny])
def list_instances(request):
    """List all available benchmark instances with their latest results."""
    from .vrp_parser import list_benchmark_files
    files = list_benchmark_files(DATASET_DIR)
    result = []
    
    import json
    # Get the single latest RUN_ALL result
    latest_run_all = BenchmarkResult.objects.filter(instance_name='RUN_ALL').order_by('-run_date').first()
    saved_all_results = latest_run_all.results_json if latest_run_all else []
    
    for f in files:
        from .vrp_parser import parse_vrp_file, parse_sol_file
        try:
            vrp = parse_vrp_file(f['vrp_path'])
            sol = parse_sol_file(f['sol_path']) if f['sol_path'] else {'cost': None}
            
            instance_data = {
                'name': f['name'],
                'dimension': vrp.get('dimension'),
                'capacity': vrp.get('capacity'),
                'num_trucks': vrp.get('num_trucks'),
                'bks': sol.get('cost') or vrp.get('optimal_value'),
                'comment': vrp.get('comment', ''),
            }
            result.append(instance_data)
        except Exception as e:
            result.append({'name': f['name'], 'error': str(e)})
            
    return Response({
        'instances': result, 
        'total': len(result),
        'has_saved_all': latest_run_all is not None,
        'last_run_date': latest_run_all.run_date if latest_run_all else None,
        'saved_all_results': saved_all_results
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def run_benchmark(request):
    """
    Run OR-Tools on a single benchmark instance and return metrics.
    POST body: { "name": "A-n32-k5", "time_limit": 15 }
    """
    from .vrp_parser import parse_vrp_file, parse_sol_file, compute_total_cost

    instance_name = request.data.get('name')
    time_limit = int(request.data.get('time_limit', 15))

    if not instance_name:
        return Response({'error': 'name is required'}, status=status.HTTP_400_BAD_REQUEST)

    vrp_path = os.path.join(DATASET_DIR, instance_name + '.vrp')
    sol_path = os.path.join(DATASET_DIR, instance_name + '.sol')

    if not os.path.exists(vrp_path):
        return Response({'error': f'Instance {instance_name} not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        vrp_data = parse_vrp_file(vrp_path)
        sol_data = parse_sol_file(sol_path) if os.path.exists(sol_path) else {'routes': [], 'cost': None}
    except Exception as e:
        return Response({'error': f'Parse error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    nodes = vrp_data['nodes']
    demands = vrp_data['demands']
    depot_id = vrp_data['depot_id']
    capacity = vrp_data['capacity']

    # BKS from .sol file or comment
    bks_cost = sol_data.get('cost') or vrp_data.get('optimal_value')

    # --- Run Baseline (Nearest Neighbor) ---
    try:
        baseline_routes, baseline_cost = compute_baseline_cost(nodes, demands, depot_id, capacity)
    except Exception as e:
        return Response({'error': f'Baseline error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- Run OR-Tools ---
    try:
        ortools_routes, ortools_cost = solve_instance_with_ortools(vrp_data, time_limit=time_limit)
    except Exception as e:
        return Response({'error': f'OR-Tools error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if ortools_routes is None:
        return Response({'error': 'OR-Tools could not find a solution'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ========== METRICS ==========
    # 1. Gap (%) vs Baseline (Nearest Neighbor)
    gap_vs_baseline = round(
        ((baseline_cost - ortools_cost) / baseline_cost * 100) if baseline_cost > 0 else 0, 2
    )

    # 2. Gap (%) vs BKS (Best Known Solution from .sol file)
    gap_vs_bks = None
    if bks_cost and bks_cost > 0:
        gap_vs_bks = round(((ortools_cost - bks_cost) / bks_cost * 100), 2)

    # 3. Fill Factor = Sum(demands assigned) / (num_vehicles_used * capacity)
    total_demand_assigned = sum(r['demand'] for r in ortools_routes)
    num_vehicles_used = len(ortools_routes)
    total_vehicle_capacity = num_vehicles_used * capacity
    fill_factor = round((total_demand_assigned / total_vehicle_capacity * 100) if total_vehicle_capacity > 0 else 0, 2)

    # 4. Density = total stops / total distance
    total_stops = sum(len(r['nodes']) for r in ortools_routes)
    density = round(total_stops / ortools_cost if ortools_cost > 0 else 0, 4)

    # 5. Distance Matrix (depot + first 20 customers to keep response small)
    all_nodes = [depot_id] + sorted([nid for nid in nodes if nid != depot_id])
    matrix_nodes = all_nodes[:21]  # depot + up to 20 customers
    matrix_labels = ['Depot'] + [f'C{nid}' for nid in matrix_nodes[1:]]
    distance_matrix = []
    for i in matrix_nodes:
        row = []
        for j in matrix_nodes:
            if i == j:
                row.append(0)
            else:
                row.append(euc_2d_distance(nodes[i], nodes[j]))
        distance_matrix.append(row)

    # 6. Per-route details
    routes_detail = []
    for idx, r in enumerate(ortools_routes):
        route_fill = round((r['demand'] / capacity * 100) if capacity > 0 else 0, 1)
        routes_detail.append({
            'route_id': idx + 1,
            'stops': r['nodes'],
            'num_stops': len(r['nodes']),
            'demand': r['demand'],
            'capacity': capacity,
            'fill_pct': route_fill,
            'distance': r['cost'],
            'density': round(len(r['nodes']) / r['cost'] if r['cost'] > 0 else 0, 4),
        })

    baseline_routes_detail = []
    for idx, r in enumerate(baseline_routes):
        route_fill = round((r['demand'] / capacity * 100) if capacity > 0 else 0, 1)
        baseline_routes_detail.append({
            'route_id': idx + 1,
            'stops': r['nodes'],
            'num_stops': len(r['nodes']),
            'demand': r['demand'],
            'capacity': capacity,
            'fill_pct': route_fill,
            'distance': r['cost'],
            'density': round(len(r['nodes']) / r['cost'] if r['cost'] > 0 else 0, 4),
        })

    # Prepare node coordinates for map visualization
    nodes_coord = []
    for nid, node in nodes.items():
        nodes_coord.append({
            'id': nid,
            'x': node['x'],
            'y': node['y'],
            'is_depot': nid == depot_id,
            'demand': demands.get(nid, 0)
        })

    response_data = {
        'instance': instance_name,
        'comment': vrp_data.get('comment', ''),
        'dimension': vrp_data.get('dimension'),
        'capacity': capacity,
        'num_trucks_available': vrp_data.get('num_trucks', 'N/A'),
        'time_limit_seconds': time_limit,
        'results': {
            'baseline_cost': baseline_cost,
            'ortools_cost': ortools_cost,
            'bks_cost': bks_cost,
            'num_vehicles_used': num_vehicles_used,
            'total_stops': total_stops,
            'total_demand': total_demand_assigned,
            'total_capacity': total_vehicle_capacity,
        },
        'metrics': {
            'gap_vs_baseline_pct': gap_vs_baseline,
            'gap_vs_bks_pct': gap_vs_bks,
            'fill_factor_pct': fill_factor,
            'density_stops_per_unit': density,
        },
        'routes': routes_detail,
        'baseline_routes': baseline_routes_detail,
        'nodes_coord': nodes_coord,
        'distance_matrix': {
            'labels': matrix_labels,
            'matrix': distance_matrix,
        }
    }

    return Response(response_data)


@api_view(['POST'])
@permission_classes([AllowAny])
def run_all_benchmarks(request):
    """
    Run OR-Tools on ALL benchmark instances and return a summary table.
    POST body: { "time_limit": 10 }
    """
    from .vrp_parser import list_benchmark_files, parse_vrp_file, parse_sol_file

    time_limit = int(request.data.get('time_limit', 10))
    files = list_benchmark_files(DATASET_DIR)
    results = []

    for f in files:
        name = f['name']
        try:
            vrp_data = parse_vrp_file(f['vrp_path'])
            sol_data = parse_sol_file(f['sol_path']) if f['sol_path'] else {'cost': None}

            nodes = vrp_data['nodes']
            demands = vrp_data['demands']
            depot_id = vrp_data['depot_id']
            capacity = vrp_data['capacity']
            bks_cost = sol_data.get('cost') or vrp_data.get('optimal_value')

            baseline_routes, baseline_cost = compute_baseline_cost(nodes, demands, depot_id, capacity)
            ortools_routes, ortools_cost = solve_instance_with_ortools(vrp_data, time_limit=time_limit)

            if ortools_routes is None:
                results.append({'name': name, 'error': 'No solution found'})
                continue

            gap_vs_baseline = round(((baseline_cost - ortools_cost) / baseline_cost * 100) if baseline_cost > 0 else 0, 2)
            gap_vs_bks = round(((ortools_cost - bks_cost) / bks_cost * 100), 2) if bks_cost else None

            total_demand = sum(r['demand'] for r in ortools_routes)
            num_vehicles = len(ortools_routes)
            fill_factor = round((total_demand / (num_vehicles * capacity) * 100) if (num_vehicles * capacity) > 0 else 0, 2)
            total_stops = sum(len(r['nodes']) for r in ortools_routes)
            density = round(total_stops / ortools_cost if ortools_cost > 0 else 0, 4)

            # Sort node IDs for consistent matrix indexing: Depot then others
            node_ids_sorted = [depot_id] + sorted([nid for nid in nodes if nid != depot_id])

            # Full coordinates
            nodes_coord = [
                {
                    'id': nid, 
                    'x': nodes[nid]['x'], 
                    'y': nodes[nid]['y'], 
                    'demand': demands.get(nid, 0), 
                    'is_depot': nid == depot_id
                } for nid in node_ids_sorted
            ]
            
            # Distance matrix for the first 21 nodes (Depot + 20 customers)
            matrix_size = min(21, len(node_ids_sorted))
            matrix_labels = [f"Depot" if nid == depot_id else f"C{nid}" for nid in node_ids_sorted[:matrix_size]]
            dist_mat = [
                [
                    round(euc_2d_distance(nodes[node_ids_sorted[i]], nodes[node_ids_sorted[j]]), 2) 
                    for j in range(matrix_size)
                ] for i in range(matrix_size)
            ]

            # Standardize routes for frontend (map 'nodes' -> 'stops', 'cost' -> 'distance')
            ortools_routes_mapped = []
            for idx, r in enumerate(ortools_routes):
                ortools_routes_mapped.append({
                    'route_id': idx + 1,
                    'stops': r['nodes'],
                    'num_stops': len(r['nodes']),
                    'distance': r['cost'],
                    'demand': r['demand'],
                    'capacity': capacity,
                    'fill_pct': round((r['demand'] / capacity * 100) if capacity > 0 else 0, 1),
                })

            baseline_routes_mapped = []
            for idx, r in enumerate(baseline_routes):
                baseline_routes_mapped.append({
                    'route_id': idx + 1,
                    'stops': r['nodes'],
                    'num_stops': len(r['nodes']),
                    'distance': r['cost'],
                    'demand': r['demand'],
                    'capacity': capacity,
                    'fill_pct': round((r['demand'] / capacity * 100) if capacity > 0 else 0, 1),
                })

            results.append({
                'name': name,
                'instance': name,
                'n': vrp_data.get('dimension', 0) - 1,
                'k': vrp_data.get('num_trucks'),
                'bks': bks_cost,
                'baseline': baseline_cost,
                'ortools': ortools_cost,
                'vehicles_used': num_vehicles,
                'gap_vs_baseline_pct': gap_vs_baseline,
                'gap_vs_bks_pct': gap_vs_bks,
                'fill_factor_pct': fill_factor,
                'density': density,
                'error': None,
                # For MetricsCard
                'results': {
                    'baseline_cost': baseline_cost,
                    'ortools_cost': ortools_cost,
                    'bks_cost': bks_cost,
                    'num_vehicles_used': num_vehicles,
                    'total_stops': total_stops,
                    'total_demand': total_demand,
                    'total_capacity': num_vehicles * capacity,
                },
                'metrics': {
                    'gap_vs_baseline_pct': gap_vs_baseline,
                    'gap_vs_bks_pct': gap_vs_bks,
                    'fill_factor_pct': fill_factor,
                    'density_stops_per_unit': density,
                },
                'routes': ortools_routes_mapped,
                'baseline_routes': baseline_routes_mapped,
                'nodes_coord': nodes_coord,
                'distance_matrix': {
                    'labels': matrix_labels,
                    'matrix': dist_mat,
                },
                'comment': f"Dimensions: {vrp_data.get('dimension', 0)}"
            })
        except Exception as e:
            results.append({'name': name, 'error': str(e)})

    # Save ALL results as a single unified record
    BenchmarkResult.objects.create(
        instance_name='RUN_ALL',
        time_limit=time_limit,
        results_json=results
    )

    return Response({'results': results, 'total': len(results)})
