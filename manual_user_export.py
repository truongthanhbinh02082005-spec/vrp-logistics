import sqlite3
import json
import uuid

def export_users_raw():
    db_path = 'backend/db.sqlite3'
    # Connect in read-only mode to bypass locks
    try:
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("Connected to DB in RO mode.")
        
        # Check table name
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Table 'users' not found.")
            return []
            
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        
        user_objects = []
        for row in rows:
            # Convert row to Django-style JSON
            fields = dict(row)
            pk = fields.pop('id')
            
            # Clean up fields that might not be in the model or need special handling
            # (Django's JSON serializer expects certain keys)
            user_objects.append({
                "model": "authentication.user",
                "pk": pk,
                "fields": fields
            })
            
        conn.close()
        print(f"Manually exported {len(user_objects)} users.")
        return user_objects
    except Exception as e:
        print(f"Error in manual export: {e}")
        return []

if __name__ == "__main__":
    users = export_users_raw()
    if users:
        # Merge with existing data.json
        data_path = 'backend/data.json'
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
            
        # Append users
        data.extend(users)
        
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Merged users into data.json")
