"""
VRP Solver using Google OR-Tools
Solves Capacitated Vehicle Routing Problem (CVRP)
"""
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math


def haversine_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points in km using Haversine formula"""
    R = 6371  
    
    lat1, lng1, lat2, lng2 = float(lat1), float(lng1), float(lat2), float(lng2)
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def create_distance_matrix(locations):
    """
    Create distance matrix from list of locations
    locations: list of dicts with 'lat' and 'lng' keys
    """
    n = len(locations)
    distance_matrix = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i != j:
                dist = haversine_distance(
                    locations[i]['lat'], locations[i]['lng'],
                    locations[j]['lat'], locations[j]['lng']
                )
                # Convert to meters and round to int (OR-Tools uses integers)
                distance_matrix[i][j] = int(dist * 1000)
    
    return distance_matrix


def solve_vrp(depot_location, order_locations, vehicle_capacities, order_demands=None):
    """
    Solve VRP using OR-Tools
    
    Args:
        depot_location: dict with 'lat', 'lng' for warehouse/depot
        order_locations: list of dicts with 'id', 'lat', 'lng' for each order
        vehicle_capacities: list of vehicle capacities (kg or volume)
        order_demands: list of order demands (weights), defaults to 1 for each
    
    Returns:
        dict with routes for each vehicle
    """
    # Combine depot + orders into locations list
    # Index 0 = depot, Index 1..n = orders
    locations = [depot_location] + order_locations
    num_locations = len(locations)
    num_vehicles = len(vehicle_capacities)
    
    if num_locations < 2:
        return {'routes': [], 'total_distance': 0, 'error': 'Not enough locations'}
    
    # Default demands: 1 unit per order
    if order_demands is None:
        order_demands = [0] + [1] * len(order_locations)  # 0 for depot
    else:
        order_demands = [0] + order_demands  # 0 for depot
    
    # Create distance matrix
    distance_matrix = create_distance_matrix(locations)
    
    # Create routing index manager
    manager = pywrapcp.RoutingIndexManager(
        num_locations,
        num_vehicles,
        0  # depot index
    )
    
    # Create routing model
    routing = pywrapcp.RoutingModel(manager)
    
    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return order_demands[from_node]
    
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        [int(c) for c in vehicle_capacities],  # Convert to integers for OR-Tools
        True,  # start cumul to zero
        'Capacity'
    )
    
    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 10  # 10 second time limit
    
    # Solve
    solution = routing.SolveWithParameters(search_parameters)
    
    if not solution:
        # Fallback: try without capacity constraints
        return solve_vrp_simple(order_locations, num_vehicles)
    
    # Extract routes
    routes = []
    total_distance = 0
    
    for vehicle_id in range(num_vehicles):
        route = []
        route_distance = 0
        index = routing.Start(vehicle_id)
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            if node_index > 0:  # Skip depot (index 0)
                # Get original order from order_locations (node_index - 1)
                order_info = order_locations[node_index - 1]
                route.append({
                    'order_id': order_info.get('id'),
                    'sequence': len(route) + 1,
                    'lat': order_info['lat'],
                    'lng': order_info['lng'],
                })
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        
        if route:  # Only add non-empty routes
            routes.append({
                'vehicle_index': vehicle_id,
                'stops': route,
                'distance_meters': route_distance,
                'distance_km': round(route_distance / 1000, 2)
            })
            total_distance += route_distance
    
    return {
        'routes': routes,
        'total_distance_km': round(total_distance / 1000, 2),
        'num_vehicles_used': len(routes),
        'algorithm': 'OR-Tools CVRP'
    }


def solve_vrp_simple(order_locations, num_vehicles):
    """
    Simple fallback: distribute orders evenly among vehicles
    Used when OR-Tools can't find a solution
    """
    routes = []
    orders_per_vehicle = len(order_locations) // num_vehicles + 1
    
    for v in range(num_vehicles):
        start = v * orders_per_vehicle
        end = min((v + 1) * orders_per_vehicle, len(order_locations))
        vehicle_orders = order_locations[start:end]
        
        if vehicle_orders:
            routes.append({
                'vehicle_index': v,
                'stops': [
                    {
                        'order_id': o.get('id'),
                        'sequence': i + 1,
                        'lat': o['lat'],
                        'lng': o['lng']
                    }
                    for i, o in enumerate(vehicle_orders)
                ],
                'distance_km': 0,  # Not calculated
            })
    
    return {
        'routes': routes,
        'total_distance_km': 0,
        'num_vehicles_used': len(routes),
        'algorithm': 'Simple Distribution (Fallback)'
    }
