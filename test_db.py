import psycopg2
import sys

print("Testing PostgreSQL connection (IPv4)...")

try:
    # Force IPv4 by using 127.0.0.1 instead of localhost
    conn = psycopg2.connect(
        host="127.0.0.1",  # Changed from localhost
        database="lemapdb",
        user="lemap",
        password="lemap123",
        port="5432"
    )
    print("✅ Connection successful!")

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ PostgreSQL version: {version[:60]}")

    cursor.execute("SELECT current_database();")
    db = cursor.fetchone()[0]
    print(f"✅ Connected to database: {db}")

    cursor.close()
    conn.close()
    print("\n✅ All tests passed!")
    sys.exit(0)

except Exception as e:
    print(f"\n❌ Connection failed!")
    print(f"Error: {e}")
    sys.exit(1)