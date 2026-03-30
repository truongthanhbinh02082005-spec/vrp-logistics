#!/bin/sh
set -e

# Wait for database if DATABASE_URL is provided (typical on Render)
echo "Checking database connection..."

python - << END
import sys
import time
import psycopg2
import os

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not set, skipping wait.")
    sys.exit(0)

print(f"Waiting for database to be ready...")
for i in range(30):
    try:
        # Psycopg2 can take the URL directly
        conn = psycopg2.connect(db_url)
        conn.close()
        print("Database is ready!")
        sys.exit(0)
    except Exception as e:
        print(f"Database not ready yet ({e}), retrying {i+1}/30...")
        time.sleep(2)
sys.exit(1)
END

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Load initial data using reliable import script
# if [ -f "data.json" ]; then
#     echo "Loading initial data from data.json using import_data.py..."
#     python import_data.py || echo "Warning: import_data.py had some errors, continuing..."
# fi


# Run collective commands and start Gunicorn
echo "Finalizing deployment and starting Gunicorn..."
python manage.py collectstatic --noinput
python manage.py migrate --noinput
exec gunicorn vrp_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-7860} \
    --workers 3 \
    --timeout 120 \
    --log-level debug \
    --access-logfile -
