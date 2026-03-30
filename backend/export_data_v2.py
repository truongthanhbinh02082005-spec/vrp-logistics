import os
import json
import sqlite3
from django.core.management import call_command
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vrp_project.settings')
django.setup()

def export_data():
    output_file = 'data.json'
    print(f"Exporting data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Using call_command directly in a script often bypasses shell/cursor issues
        call_command('dumpdata', 
                     indent=2, 
                     exclude=['auth.permission', 'contenttypes'], 
                     stdout=f)
    print("Export successful!")

if __name__ == "__main__":
    try:
        export_data()
    except Exception as e:
        print(f"Error during export: {e}")
