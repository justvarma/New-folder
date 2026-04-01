import time
import redis
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# ============ REDIS CONNECTION ============
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)

# ============ POSTGRES CONNECTION ============
def get_db_connection():
    """Create a fresh DB connection"""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "lemapdb"),
        user=os.getenv("DB_USER", "lemap"),
        password=os.getenv("DB_PASSWORD", "lemap123"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

# ============ CONSTANTS ============
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
HUB_RED_DURATION = 900     # Hub stays RED for 15 minutes

print("=" * 60)
print("🚀 LEMAP Event Processor Started Successfully")
print("=" * 60)
print(f"⚙️  Spike Threshold: {SPIKE_THRESHOLD} events")
print(f"⏱️  Check Interval: {CHECK_INTERVAL} seconds")
print(f"🔴 Hub RED Duration: {HUB_RED_DURATION} seconds")
print(f"🎯 Monitoring Hubs: {', '.join(HUBS)}")
print("=" * 60)

# ============ MAIN LOOP ============
loop_count = 0

while True:
    loop_count += 1
    print(f"\n[Loop #{loop_count}] Checking for spikes...")

    alerts_generated = 0

    for event_type in EVENT_TYPES:
        for hub in HUBS:
            redis_key = f"event_count:{event_type}:{hub}"

            try:
                count = redis_client.get(redis_key)

                if count and int(count) >= SPIKE_THRESHOLD:
                    # Get fresh connection for each alert
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    message = f"⚠️ Spike detected: {count} {event_type} events at {hub}"

                    try:
                        # Insert alert
                        cursor.execute(
                            """
                            INSERT INTO alert (hub, event_type, message)
                            VALUES (%s, %s, %s)
                            """,
                            (hub, event_type, message)
                        )
                        conn.commit()

                        # Mark hub as RED in Redis
                        redis_client.set(f"hub_status:{hub}", "red", ex=HUB_RED_DURATION)

                        # Reset counter
                        redis_client.delete(redis_key)

                        alerts_generated += 1
                        print(f"  🚨 ALERT: {hub} | {event_type} | Count: {count}")

                    except Exception as e:
                        conn.rollback()
                        print(f"  ❌ Error generating alert: {e}")

                    finally:
                        cursor.close()
                        conn.close()

            except Exception as e:
                print(f"  ❌ Error checking {event_type} at {hub}: {e}")

    if alerts_generated > 0:
        print(f"✅ Generated {alerts_generated} alert(s)")
    else:
        print("✅ No spikes detected")

    time.sleep(CHECK_INTERVAL)