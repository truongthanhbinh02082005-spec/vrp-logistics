"""
Parser for CVRP benchmark files in TSPLIB format (.vrp and .sol)
Supports the Augerat A-series benchmark instances.
"""
import math
import os
import re


def parse_vrp_file(filepath):
    """
    Parse a .vrp file in TSPLIB format.
    Returns a dict with: name, comment, dimension, capacity, 
    nodes (id, x, y), demands (id -> demand), depot_id, optimal_value
    """
    with open(filepath, 'r') as f:
        content = f.read()

    result = {}

    # Extract metadata
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('NAME'):
            result['name'] = line.split(':', 1)[-1].strip()
        elif line.startswith('COMMENT'):
            comment = line.split(':', 1)[-1].strip()
            result['comment'] = comment
            # Try to extract optimal value from comment like "(Augerat et al, ...Optimal value: 784)"
            m = re.search(r'[Oo]ptimal\s*value\s*[:\=]\s*(\d+)', comment)
            if m:
                result['optimal_value'] = int(m.group(1))
            # Try "No of trucks: 5"
            m2 = re.search(r'No of trucks\s*[:\=]\s*(\d+)', comment, re.IGNORECASE)
            if m2:
                result['num_trucks'] = int(m2.group(1))
        elif line.startswith('DIMENSION'):
            result['dimension'] = int(line.split(':', 1)[-1].strip())
        elif line.startswith('CAPACITY'):
            result['capacity'] = int(line.split(':', 1)[-1].strip())

    # Parse sections
    lines = content.splitlines()
    mode = None
    nodes = {}
    demands = {}
    depot_ids = []

    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('NODE_COORD_SECTION'):
            mode = 'nodes'
            continue
        elif line_stripped.startswith('DEMAND_SECTION'):
            mode = 'demands'
            continue
        elif line_stripped.startswith('DEPOT_SECTION'):
            mode = 'depot'
            continue
        elif line_stripped == 'EOF':
            mode = None
            continue

        if not line_stripped or line_stripped == '-1':
            if mode == 'depot':
                mode = None
            continue

        try:
            if mode == 'nodes':
                parts = line_stripped.split()
                node_id = int(parts[0])
                x, y = float(parts[1]), float(parts[2])
                nodes[node_id] = {'id': node_id, 'x': x, 'y': y}
            elif mode == 'demands':
                parts = line_stripped.split()
                node_id, demand = int(parts[0]), int(parts[1])
                demands[node_id] = demand
            elif mode == 'depot':
                val = int(line_stripped)
                if val > 0:
                    depot_ids.append(val)
        except (ValueError, IndexError):
            pass

    result['nodes'] = nodes
    result['demands'] = demands
    result['depot_id'] = depot_ids[0] if depot_ids else 1
    return result


def parse_sol_file(filepath):
    """
    Parse a .sol file with known best solution.
    Returns dict with: routes (list of list of node ids), cost
    """
    routes = []
    cost = None

    if not os.path.exists(filepath):
        return {'routes': [], 'cost': None}

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('Route'):
                # "Route #1: 21 31 19 17 13 7 26"
                route_part = line.split(':', 1)[-1].strip()
                route_nodes = [int(x) for x in route_part.split()]
                routes.append(route_nodes)
            elif line.lower().startswith('cost'):
                try:
                    cost = int(line.split()[-1])
                except ValueError:
                    pass

    return {'routes': routes, 'cost': cost}


def euc_2d_distance(n1, n2):
    """Euclidean 2D distance (rounded to nearest int as per TSPLIB spec)"""
    dx = n1['x'] - n2['x']
    dy = n1['y'] - n2['y']
    return int(math.sqrt(dx * dx + dy * dy) + 0.5)


def compute_route_cost(route_node_ids, nodes, depot_id):
    """Compute total distance for a single route (depot -> stops -> depot)"""
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


def compute_total_cost(routes, nodes, depot_id):
    """Compute total cost for all routes"""
    return sum(compute_route_cost(r, nodes, depot_id) for r in routes)


def list_benchmark_files(dataset_dir):
    """List all .vrp files in the dataset directory"""
    files = []
    if not os.path.isdir(dataset_dir):
        return files
    for fname in sorted(os.listdir(dataset_dir)):
        if fname.endswith('.vrp'):
            base = fname[:-4]
            sol_path = os.path.join(dataset_dir, base + '.sol')
            files.append({
                'name': base,
                'vrp_path': os.path.join(dataset_dir, fname),
                'sol_path': sol_path if os.path.exists(sol_path) else None,
            })
    return files
