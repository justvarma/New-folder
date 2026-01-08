import time
import redis
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

print("🚀 LEMAP Event Processor starting...")

# ---------------- REDIS CONNECTION ----------------
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True
    )
    redis_client.ping()
    print("✅ Redis connected")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    exit(1)

# ---------------- POSTGRES CONNECTION ----------------
try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "lemapdb"),
        user=os.getenv("DB_USER", "lemap"),
        password=os.getenv("DB_PASSWORD", "lemap123"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    cursor = conn.cursor()
    print("✅ PostgreSQL connected")
except Exception as e:
    print(f"❌ PostgreSQL connection failed: {e}")
    exit(1)

# ---------------- CONSTANTS ----------------
EVENT_TYPES = [
    "ORDER_DELAYED",
    "DELIVERY_FAILED",
    "INVENTORY_LOW",
    "VEHICLE_BREAKDOWN",
    "ROUTE_BLOCKED",
    "HUB_OVERLOAD"
]

HUBS = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad"]

SPIKE_THRESHOLD = 3        # Number of events to trigger alert
CHECK_INTERVAL = 30        # Check every 30 seconds
ALERT_COOLDOWN = 900       # 15 minutes cooldown for same alert

print(f"📊 Monitoring {len(HUBS)} hubs for {len(EVENT_TYPES)} event types")
print(f"⚡ Spike threshold: {SPIKE_THRESHOLD} events")
print(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
print("="*60)

# ---------------- MAIN LOOP ----------------
alert_count = 0

while True:
    try:
        for event_type in EVENT_TYPES:
            for hub in HUBS:
                redis_key = f"event_count:{event_type}:{hub}"
                count = redis_client.get(redis_key)

                if count and int(count) >= SPIKE_THRESHOLD:
                    # Check if we already alerted recently (cooldown)
                    cooldown_key = f"alert_cooldown:{event_type}:{hub}"
                    if redis_client.exists(cooldown_key):
                        continue  # Skip, already alerted recently

                    # Generate alert message
                    message = f"Spike detected: {count} {event_type} events at {hub} hub"

                    # Insert alert into database
                    try:
                        cursor.execute(
                            """
                            INSERT INTO alert (hub, event_type, message)
                            VALUES (%s, %s, %s)
                            """,
                            (hub, event_type, message)
                        )
                        conn.commit()

                        # Set hub status to RED
                        redis_client.set(f"hub_status:{hub}", "red", ex=ALERT_COOLDOWN)

                        # Set cooldown to prevent duplicate alerts
                        redis_client.set(cooldown_key, "1", ex=ALERT_COOLDOWN)

                        # Reset counter
                        redis_client.delete(redis_key)

                        alert_count += 1
                        print(f"🚨 ALERT #{alert_count} → {hub} | {event_type} | Count: {count}")

                    except Exception as e:
                        print(f"❌ Error creating alert: {e}")
                        conn.rollback()

    except Exception as e:
        print(f"❌ Error in main loop: {e}")
        time.sleep(5)  # Wait before retrying

    time.sleep(CHECK_INTERVAL)