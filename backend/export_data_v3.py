import os
import json
import django
from django.core import serializers

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vrp_project.settings')
django.setup()

def export_essential_data():
    output_file = 'data.json'
    print(f"Exporting essential data to {output_file}...")
    
    # List of apps to export (excluding problematic ones)
    apps_to_export = [
        'authentication',
        'orders',
        'vehicles',
        'drivers',
        'warehouses',
        'transport',
        'benchmark',
        'transactions',
        'reports'
    ]
    
    all_objects = []
    
    from django.apps import apps
    for app_label in apps_to_export:
        try:
            app_config = apps.get_app_config(app_label)
            for model in app_config.get_models():
                print(f"  Exporting {app_label}.{model.__name__}...")
                queryset = model.objects.all()
                data = serializers.serialize('json', queryset)
                all_objects.extend(json.loads(data))
        except Exception as e:
            print(f"  Skipping {app_label}: {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_objects, f, indent=2, ensure_ascii=False)
        
    print(f"Export successful! Total objects: {len(all_objects)}")

if __name__ == "__main__":
    export_essential_data()
