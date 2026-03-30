import os
import django
import sys
import json

# Add the current directory to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vrp_project.settings")
django.setup()

from django.core import serializers
from django.apps import apps

# List of models to export in order (respecting dependencies)
models_to_export = [
    'authentication.User',
    'warehouses.Warehouse',
    'vehicles.Vehicle',
    'orders.Order',
    'transport.Route',
    'transport.RouteStop',
    'transactions.Transaction',
    'benchmark.BenchmarkResult',
]

all_data = []

print("Starting model-by-model export...")

for model_path in models_to_export:
    try:
        model = apps.get_model(model_path)
        print(f"Exporting {model_path}...")
        
        # Serialize model objects
        data_str = serializers.serialize("json", model.objects.all())
        data_list = json.loads(data_str)
        all_data.extend(data_list)
        
        print(f"  Successfully exported {len(data_list)} objects.")
    except Exception as e:
        print(f"  Error exporting {model_path}: {e}")

# Write combined data to data.json
try:
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print("\nSuccessfully wrote all data to data.json")
except Exception as e:
    print(f"\nError writing data.json: {e}")
