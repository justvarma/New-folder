from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LEMAP Dashboard API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ CONFIG ============
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "database": os.getenv("DB_NAME", "lemapdb"),
    "user": os.getenv("DB_USER", "lemap"),
    "password": os.getenv("DB_PASSWORD", "lemap123"),
    "port": os.getenv("DB_PORT", "5432")
}

REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "127.0.0.1"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "decode_responses": True
}

# Valid hubs
VALID_HUBS = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad"]

# ============ DATABASE ============
def get_db_connection():
    """PostgreSQL connection with error handling"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"DB connection failed: {str(e)}"
        )

# ============ REDIS ============
def get_redis_connection():
    """Redis connection with error handling"""
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()
        return r
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Redis connection failed: {str(e)}"
        )

# ============ ENDPOINTS ============

@app.get("/events")
async def get_events(
        hub: Optional[str] = Query(None, description="Filter by hub (e.g., Delhi)"),
        limit: int = Query(100, description="Max number of events to return")
):
    """
    GET /events - Get all events

    Optional Query Parameters:
    - hub: Filter by specific hub (Delhi, Mumbai, Bangalore, Chennai, Hyderabad)
    - limit: Maximum number of events (default: 100)

    Example:
    - /events
    - /events?hub=Delhi
    - /events?hub=Delhi&limit=50
    """
    # Validate hub if provided
    if hub and hub not in VALID_HUBS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid hub. Must be one of: {', '.join(VALID_HUBS)}"
        )

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Build query
        if hub:
            query = """
                SELECT id, event_type, hub, description, timestamp 
                FROM event 
                WHERE hub = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            cursor.execute(query, (hub, limit))
        else:
            query = """
                SELECT id, event_type, hub, description, timestamp 
                FROM event 
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            cursor.execute(query, (limit,))

        events = cursor.fetchall()

        # Convert timestamp to ISO format string
        for event in events:
            if isinstance(event['timestamp'], datetime):
                event['timestamp'] = event['timestamp'].isoformat()

        return events

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching events: {str(e)}"
        )

    finally:
        cursor.close()
        conn.close()


@app.get("/alerts")
async def get_alerts(
        hub: Optional[str] = Query(None, description="Filter by hub (e.g., Delhi)"),
        limit: int = Query(100, description="Max number of alerts to return")
):
    """
    GET /alerts - Get all alerts

    Optional Query Parameters:
    - hub: Filter by specific hub (Delhi, Mumbai, Bangalore, Chennai, Hyderabad)
    - limit: Maximum number of alerts (default: 100)

    Example:
    - /alerts
    - /alerts?hub=Delhi
    - /alerts?hub=Delhi&limit=50
    """
    # Validate hub if provided
    if hub and hub not in VALID_HUBS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid hub. Must be one of: {', '.join(VALID_HUBS)}"
        )

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Build query
        if hub:
            query = """
                SELECT id, hub, event_type, message, timestamp 
                FROM alert 
                WHERE hub = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            cursor.execute(query, (hub, limit))
        else:
            query = """
                SELECT id, hub, event_type, message, timestamp 
                FROM alert 
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            cursor.execute(query, (limit,))

        alerts = cursor.fetchall()

        # Convert timestamp to ISO format string
        for alert in alerts:
            if isinstance(alert['timestamp'], datetime):
                alert['timestamp'] = alert['timestamp'].isoformat()

        return alerts

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching alerts: {str(e)}"
        )

    finally:
        cursor.close()
        conn.close()


@app.get("/hub-status")
async def get_hub_status():
    """
    GET /hub-status - Get health status for all hubs

    Returns:
    {
        "Delhi": "green" or "red",
        "Mumbai": "green" or "red",
        "Bangalore": "green" or "red",
        "Chennai": "green" or "red",
        "Hyderabad": "green" or "red"
    }

    - green: Hub is operational
    - red: Hub has active alerts
    """
    try:
        r = get_redis_connection()

        status = {}
        for hub in VALID_HUBS:
            redis_key = f"hub_status:{hub}"
            hub_status = r.get(redis_key)

            # Default to green if not set
            status[hub] = hub_status if hub_status in ["green", "red"] else "green"

        return status

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching hub status: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 LEMAP Dashboard API")
    print("=" * 60)
    print("📡 Available Endpoints:")
    print("   GET  /events       - Get all events")
    print("   GET  /alerts       - Get all alerts")
    print("   GET  /hub-status   - Get hub health status")
    print("=" * 60)
    print("🌐 Server: http://localhost:8001")
    print("📖 Docs: http://localhost:8001/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8001)