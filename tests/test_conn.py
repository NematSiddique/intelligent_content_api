import psycopg2

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="admin",
        password="secret",
        dbname="contentdb"
    )
except Exception as e:
    print("❌ Connection failed:", e)
