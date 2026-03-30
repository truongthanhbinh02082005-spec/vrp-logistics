import os
import json
import psycopg2
from decouple import config

def export_users_psycopg2():
    try:
        # Load from .env via decouple
        dbname = config('DB_NAME')
        user = config('DB_USER')
        password = config('DB_PASSWORD')
        host = config('DB_HOST')
        port = config('DB_PORT')
        
        print(f"Connecting to PostgreSQL: {dbname}...")
        conn = psycopg2.connect(
            dbname=dbname, user=user, password=password, 
            host=host, port=port
        )
        cur = conn.cursor()
        
        # Get column names
        cur.execute("SELECT * FROM users LIMIT 0")
        colnames = [desc[0] for desc in cur.description]
        
        # Get data
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        
        user_objects = []
        for row in rows:
            data = dict(zip(colnames, row))
            pk = str(data.pop('id'))  # UUID to string
            
            # Remove any non-model fields if they exist
            # Convert datetime objects to ISO strings for JSON
            for k, v in data.items():
                if hasattr(v, 'isoformat'):
                    data[k] = v.isoformat()
            
            user_objects.append({
                "model": "authentication.user",
                "pk": pk,
                "fields": data
            })
            
        cur.close()
        conn.close()
        print(f"Successfully exported {len(user_objects)} users via psycopg2.")
        return user_objects
    except Exception as e:
        print(f"Error in psycopg2 export: {e}")
        return []

if __name__ == "__main__":
    # Change to backend dir to pick up .env
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    users = export_users_psycopg2()
    if users:
        data_path = 'data.json'
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter out any existing users to avoid duplicates
        data = [obj for obj in data if obj['model'] != 'authentication.user']
        data.extend(users)
        
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Merged {len(users)} users into data.json")
