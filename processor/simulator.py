import time
import random
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000/event")
API_KEY = os.getenv("API_KEY", "your-secret-key-here")

EVENT_TYPES = [
    "ORDER_DELAYED",
    "DELIVERY_FAILED",
    "INVENTORY_LOW",
    "VEHICLE_BREAKDOWN",
    "ROUTE_BLOCKED",
    "HUB_OVERLOAD"
]

HUBS = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad"]

DESCRIPTIONS = {
    "ORDER_DELAYED": [
        "Traffic congestion causing delays",
        "Weather conditions affecting delivery",
        "Vehicle breakdown en route",
        "Customer unavailable at address"
    ],
    "DELIVERY_FAILED": [
        "Address not found",
        "Customer refused package",
        "Access denied to delivery location",
        "Package damaged in transit"
    ],
    "INVENTORY_LOW": [
        "Stock running low for popular items",
        "Supplier delay affecting inventory",
        "High demand depleting stock",
        "Warehouse capacity issues"
    ],
    "VEHICLE_BREAKDOWN": [
        "Engine failure reported",
        "Flat tire on delivery route",
        "Mechanical issues detected",
        "Vehicle accident reported"
    ],
    "ROUTE_BLOCKED": [
        "Road construction blocking route",
        "Protest/demonstration on main road",
        "Accident causing traffic jam",
        "Flooding on delivery route"
    ],
    "HUB_OVERLOAD": [
        "Package sorting capacity exceeded",
        "Staff shortage causing delays",
        "System processing backlog",
        "Peak season volume surge"
    ]
}

print("🎲 LEMAP Event Simulator")
print(f"📡 Gateway: {GATEWAY_URL}")
print(f"🏢 Hubs: {', '.join(HUBS)}")
print(f"📊 Event types: {len(EVENT_TYPES)}")
print("="*60)

event_count = 0
error_count = 0

while True:
    try:
        # Random event generation
        event_type = random.choice(EVENT_TYPES)
        hub = random.choice(HUBS)
        description = random.choice(DESCRIPTIONS[event_type])

        # Payload
        payload = {
            "event_type": event_type,
            "hub": hub,
            "description": description
        }

        # Headers
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }

        # Send event to gateway
        response = requests.post(
            GATEWAY_URL,
            json=payload,
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            event_count += 1
            print(f"✅ Event #{event_count}: {hub:12} | {event_type:20} | {response.json().get('event_id')}")
        else:
            error_count += 1
            print(f"❌ Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        error_count += 1
        print(f"❌ Connection error: {e}")

    except Exception as e:
        error_count += 1
        print(f"❌ Unexpected error: {e}")

    # Random delay between 5-15 seconds
    delay = random.randint(5, 15)
    time.sleep(delay)