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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "lemapdb"),
    "user": os.getenv("DB_USER", "lemap"),
    "password": os.getenv("DB_PASSWORD", "lemap123"),
    "port": os.getenv("DB_PORT", "5432")
}

REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "decode_responses": True
}

VALID_HUBS = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad"]

def get_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {str(e)}")

def get_redis():
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()
        return r
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "service": "LEMAP Dashboard API",
        "status": "running",
        "endpoints": ["/alerts", "/hub-status", "/events", "/stats"]
    }

@app.get("/alerts")
async def get_alerts(
        hub: Optional[str] = Query(None, description="Filter by hub"),
        limit: int = Query(50, description="Max results")
):
    """
    GET /alerts - Fetch alerts from database
    """
    if hub and hub not in VALID_HUBS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid hub. Must be one of: {', '.join(VALID_HUBS)}"
        )

    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
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

        # Convert timestamps
        for alert in alerts:
            if isinstance(alert['timestamp'], datetime):
                alert['timestamp'] = alert['timestamp'].isoformat()

        return alerts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

    finally:
        cursor.close()
        conn.close()

@app.get("/hub-status")
async def get_hub_status():
    """
    GET /hub-status - Get real-time hub health status
    Returns: {"Delhi": "green", "Mumbai": "red", ...}
    """
    try:
        r = get_redis()
        status = {}

        for hub in VALID_HUBS:
            redis_key = f"hub_status:{hub}"
            hub_status = r.get(redis_key)

            # Default to green if not set
            status[hub] = hub_status if hub_status in ["green", "red"] else "green"

        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hub status: {str(e)}")

@app.get("/events")
async def get_events(
        hub: Optional[str] = Query(None, description="Filter by hub"),
        event_type: Optional[str] = Query(None, description="Filter by event type"),
        limit: int = Query(100, description="Max results")
):
    """
    GET /events - Fetch events from database
    """
    if hub and hub not in VALID_HUBS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid hub. Must be one of: {', '.join(VALID_HUBS)}"
        )

    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        conditions = []
        params = []

        if hub:
            conditions.append("hub = %s")
            params.append(hub)

        if event_type:
            conditions.append("event_type = %s")
            params.append(event_type)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)

        query = f"""
            SELECT id, event_type, hub, description, timestamp
            FROM event
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT %s
        """

        cursor.execute(query, params)
        events = cursor.fetchall()

        # Convert timestamps
        for event in events:
            if isinstance(event['timestamp'], datetime):
                event['timestamp'] = event['timestamp'].isoformat()

        return events

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

    finally:
        cursor.close()
        conn.close()

@app.get("/stats")
async def get_stats():
    """
    GET /stats - Get system statistics
    """
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Total events
        cursor.execute("SELECT COUNT(*) as total FROM event")
        total_events = cursor.fetchone()['total']

        # Total alerts
        cursor.execute("SELECT COUNT(*) as total FROM alert")
        total_alerts = cursor.fetchone()['total']

        # Events by hub
        cursor.execute("""
            SELECT hub, COUNT(*) as count
            FROM event
            GROUP BY hub
            ORDER BY count DESC
        """)
        events_by_hub = cursor.fetchall()

        # Recent alerts by hub
        cursor.execute("""
            SELECT hub, COUNT(*) as count
            FROM alert
            WHERE timestamp > NOW() - INTERVAL '1 hour'
            GROUP BY hub
            ORDER BY count DESC
        """)
        recent_alerts_by_hub = cursor.fetchall()

        return {
            "total_events": total_events,
            "total_alerts": total_alerts,
            "events_by_hub": events_by_hub,
            "recent_alerts_by_hub": recent_alerts_by_hub
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)