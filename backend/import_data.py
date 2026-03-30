import os
import sys
import django
from django.core import serializers
from django.db import transaction

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE_DIR, 'backend')):
    BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
else:
    BACKEND_DIR = BASE_DIR

sys.path.append(BACKEND_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vrp_project.settings')
django.setup()

def import_data(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Importing data from {file_path} using Django deserializer...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data_str = f.read()

    # Use standard Django deserializer
    try:
        objects = list(serializers.deserialize('json', data_str))
        count = len(objects)
        print(f"  Deserialized {count} objects.")
        
        with transaction.atomic():
            for obj in objects:
                # obj is a DeserializedObject, call save() to persist
                obj.save()
        
        print("Import completed successfully!")
    except Exception as e:
        print(f"Error during import: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    data_file = os.path.join(BACKEND_DIR, 'data.json')
    import_data(data_file)
