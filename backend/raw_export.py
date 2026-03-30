import psycopg2
import json
import uuid
import datetime

import decimal

def default_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

try:
    conn = psycopg2.connect(dbname="vrp_logistics", user="postgres", password="123456", host="localhost")
    cur = conn.cursor()
    
    # Define models and their tables
    # Format: model_name: {table: table_name, m2m: {field_name: junction_table}}
    models_config = {
        'authentication.user': {'table': 'users'},
        'warehouses.warehouse': {'table': 'warehouses'},
        'vehicles.vehicle': {'table': 'vehicles'},
        'orders.order': {
            'table': 'orders',
            'm2m': {'drivers': 'orders_drivers', 'order_id': 'user_id'}
        },
        'transport.route': {
            'table': 'routes',
            'm2m': {'drivers': 'routes_drivers', 'route_id': 'user_id'}
        },
        'transport.routestop': {'table': 'route_stops'},
        'transactions.transaction': {'table': 'transactions'},
        'benchmark.benchmarkresult': {'table': 'benchmark_results'}
    }
    
    all_data = []
    
    for model_name, config in models_config.items():
        table_name = config['table']
        try:
            # Check table existence
            cur.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}');")
            if not cur.fetchone()[0]:
                print(f"Skipping {model_name}: table {table_name} does not exist")
                continue
            
            cur.execute(f"SELECT * FROM {table_name};")
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            
            for row in rows:
                obj_dict = dict(zip(colnames, row))
                pk = str(obj_dict.get('id', ''))
                fields = {k: v for k, v in obj_dict.items() if k != 'id'}
                
                # Handle M2M
                if 'm2m' in config:
                    for field_name, junction_info in config['m2m'].items():
                        # This is a bit simplified, assuming 1 junction table per model for now
                        pass
                
                all_data.append({
                    "model": model_name,
                    "pk": pk,
                    "fields": fields
                })
            print(f"Exported {len(rows)} from {table_name} ({model_name})")
        except Exception as e:
            print(f"Error exporting {model_name}: {e}")
            conn.rollback()

    # Special handling for M2M: Orders and Routes drivers
    # Fetching junction table data separately and appending to fields
    # For Orders
    cur.execute("SELECT order_id, user_id FROM orders_drivers;")
    order_drivers = {}
    for oid, uid in cur.fetchall():
        order_drivers.setdefault(str(oid), []).append(str(uid))
    
    # For Routes
    cur.execute("SELECT route_id, user_id FROM routes_drivers;")
    route_drivers = {}
    for rid, uid in cur.fetchall():
        route_drivers.setdefault(str(rid), []).append(str(uid))
        
    for entry in all_data:
        if entry['model'] == 'orders.order':
            entry['fields']['drivers'] = order_drivers.get(entry['pk'], [])
        elif entry['model'] == 'transport.route':
            entry['fields']['drivers'] = route_drivers.get(entry['pk'], [])

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, default=default_serializer)
    
    print("Successfully exported all data to data.json")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
