import json
import os

def scrub_data(input_file='backend/data.json'):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    # Map of models and their integer fields that need scrubbing
    integer_field_map = {
        'vehicles.vehicle': ['capacity_kg'],
        'warehouses.warehouse': ['total_volume', 'used_volume'],
        'transport.route': ['total_time', 'total_orders'],
        'transport.routestop': ['sequence', 'time_from_previous']
    }

    print(f"Scrubbing {input_file} for type mismatches...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scrubbed_count = 0
    for obj in data:
        model = obj.get('model', '')
        fields = obj.get('fields', {})
        
        if model in integer_field_map:
            int_fields = integer_field_map[model]
            for field_name in int_fields:
                if field_name in fields:
                    val = fields[field_name]
                    # Handle string floats like "3000.00" or actual floats like 3000.0
                    original_val = val
                    new_val = None
                    
                    if isinstance(val, str) and '.' in val:
                        try:
                            new_val = int(float(val))
                        except ValueError:
                            pass
                    elif isinstance(val, float):
                        new_val = int(val)
                    
                    if new_val is not None and new_val != original_val:
                        fields[field_name] = new_val
                        scrubbed_count += 1
                        print(f"  Fixed {model}.{field_name}: {original_val} -> {new_val}")

    if scrubbed_count > 0:
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Scrubbing complete! Fixed {scrubbed_count} field values.")
    else:
        print("No issues found to scrub.")

if __name__ == "__main__":
    scrub_data()
