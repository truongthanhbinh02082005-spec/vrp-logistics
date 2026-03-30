import os
import sys
import json
import django
from django.core import serializers

# Setup Django environment relative to this script in backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vrp_project.settings')
django.setup()

def export_and_scrub():
    output_file = os.path.join(BASE_DIR, 'data.json')
    print(f"Generating fresh data fixture from PostgreSQL: {output_file}...")
    
    apps_to_export = [
        'authentication', 'orders', 'vehicles', 
        'warehouses', 'transport', 'benchmark', 
        'transactions', 'reports'
    ]
    
    integer_field_map = {
        'vehicles.vehicle': ['capacity_kg'],
        'warehouses.warehouse': ['total_volume', 'used_volume'],
        'transport.route': ['total_time', 'total_orders'],
        'transport.routestop': ['sequence', 'time_from_previous'],
        'benchmark.benchmarkresult': ['time_limit']
    }
    
    all_objects = []
    from django.apps import apps
    
    for app_label in apps_to_export:
        try:
            app_config = apps.get_app_config(app_label)
            for model in app_config.get_models():
                model_name = f"{app_label}.{model.__name__}".lower()
                print(f"  Processing {model_name}...")
                
                queryset = model.objects.all()
                # Loading to list to avoid cursor reuse/concurrency issues
                object_list = list(queryset)
                if not object_list:
                    continue
                    
                serialized = serializers.serialize('json', object_list)
                objects = json.loads(serialized)
                
                # Immediate scrubbing
                for obj in objects:
                    fields = obj.get('fields', {})
                    if model_name in integer_field_map:
                        for field in integer_field_map[model_name]:
                            if field in fields:
                                val = fields[field]
                                if val is not None:
                                    try:
                                        fields[field] = int(float(val))
                                    except:
                                        pass
                
                all_objects.extend(objects)
        except Exception as e:
            print(f"  Skipping {app_label}: {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_objects, f, indent=2, ensure_ascii=False)
        
    print(f"Success! Exported {len(all_objects)} objects to UTF-8 {output_file}")

if __name__ == "__main__":
    export_and_scrub()
