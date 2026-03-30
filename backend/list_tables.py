import psycopg2

try:
    conn = psycopg2.connect(dbname="vrp_logistics", user="postgres", password="123456", host="localhost")
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cur.fetchall()
    for table in tables:
        table_name = table[0]
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cur.fetchone()[0]
        if count > 0:
            print(f"{table_name}: {count} rows")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
