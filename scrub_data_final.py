import json
import os

def scrub_data(input_file='backend/data.json'):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    # Comprehensive map of all models and their IntegerField variants
    integer_field_map = {
        'vehicles.vehicle': ['capacity_kg'],
        'warehouses.warehouse': ['total_volume', 'used_volume'],
        'transport.route': ['total_time', 'total_orders'],
        'transport.routestop': ['sequence', 'time_from_previous'],
        'benchmark.benchmarkresult': ['time_limit'],
        'auth.user': ['is_superuser', 'is_staff', 'is_active'], # Booleans are ints in some contexts, but usually handled.
        # Adding any other potential hidden ones from migrations
        'authentication.user': [], # Checked, no IntegerFields
        'orders.order': [],        # Checked, no IntegerFields (volume/weight are Decimal)
    }

    print(f"Scrubbing {input_file} for type mismatches...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scrubbed_count = 0
    detailed_fixes = []

    for obj in data:
        model = obj.get('model', '').lower()
        fields = obj.get('fields', {})
        
        if model in integer_field_map:
            int_fields = integer_field_map[model]
            for field_name in int_fields:
                if field_name in fields:
                    val = fields[field_name]
                    if val is None:
                        continue
                        
                    original_val = val
                    new_val = None
                    
                    # Handle string floats like "1000.00"
                    if isinstance(val, str) and '.' in val:
                        try:
                            # Try converting to float then int to handle ".00"
                            new_val = int(float(val))
                        except (ValueError, TypeError):
                            pass
                    # Handle actual floats like 1000.0
                    elif isinstance(val, float):
                        new_val = int(val)
                    
                    if new_val is not None and new_val != original_val:
                        fields[field_name] = new_val
                        scrubbed_count += 1
                        detailed_fixes.append(f"  Fixed {model}.{field_name}: {original_val} -> {new_val}")

    if scrubbed_count > 0:
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Scrubbing complete! Fixed {scrubbed_count} field values.")
        for fix in detailed_fixes:
            print(fix)
    else:
        print("No issues found to scrub.")

if __name__ == "__main__":
    scrub_data()
