# 🪟 LEMAP - Windows Setup Guide

**Real-time Logistics Event Monitoring & Alerting Platform for Windows**

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the System](#running-the-system)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Quick Commands](#quick-commands)

---

## 📦 Prerequisites

### Required Software

1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - After installation, restart your computer
   - Ensure Docker Desktop is running (whale icon in system tray)

2. **Python 3.8+**
   - Download: https://www.python.org/downloads/
   - ⚠️ **Important**: Check "Add Python to PATH" during installation

3. **Node.js 16+**
   - Download: https://nodejs.org/
   - Choose LTS version

4. **Git** (optional, for cloning)
   - Download: https://git-scm.com/download/win

### Verify Installation

Open **PowerShell** and run:

```powershell
docker --version
python --version
node --version
npm --version
```

---

## 🚀 Installation

### Step 1: Clone/Download Project

```powershell
# If using Git
git clone <your-repo-url>
cd lemap-project

# Or download ZIP and extract
```

### Step 2: Create Required Files

#### Create `init.sql` in root folder:

```sql
-- Drop existing tables
DROP TABLE IF EXISTS alert CASCADE;
DROP TABLE IF EXISTS event CASCADE;

-- Create events table
CREATE TABLE event (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    hub VARCHAR(50) NOT NULL,
    description TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create alerts table
CREATE TABLE alert (
    id SERIAL PRIMARY KEY,
    hub VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_event_hub ON event(hub);
CREATE INDEX idx_event_type ON event(event_type);
CREATE INDEX idx_event_timestamp ON event(timestamp DESC);
CREATE INDEX idx_alert_hub ON alert(hub);
CREATE INDEX idx_alert_timestamp ON alert(timestamp DESC);
```

#### Create `.env` files:

**gateway/.env:**
```env
DB_HOST=127.0.0.1
DB_NAME=lemapdb
DB_USER=lemap
DB_PASSWORD=lemap123
DB_PORT=5432
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
API_KEY=lemap-secret-key-2024
```

**processor/.env:**
```env
DB_HOST=127.0.0.1
DB_NAME=lemapdb
DB_USER=lemap
DB_PASSWORD=lemap123
DB_PORT=5432
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
API_KEY=lemap-secret-key-2024
```

**api/.env:**
```env
DB_HOST=127.0.0.1
DB_NAME=lemapdb
DB_USER=lemap
DB_PASSWORD=lemap123
DB_PORT=5432
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

**HACKATHON/.env:**
```env
VITE_API_BASE=http://localhost:8001
VITE_ALERTS_BASE=http://localhost:8001
```

### Step 3: Verify docker-compose.yml

Ensure your `docker-compose.yml` looks like this:

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15
    container_name: lemap_postgres
    environment:
      POSTGRES_DB: lemapdb
      POSTGRES_USER: lemap
      POSTGRES_PASSWORD: lemap123
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7
    container_name: lemap_redis
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  pgdata:
```

### Step 4: Start Docker Services

```powershell
# Start Docker containers
docker-compose up -d

# Wait 20 seconds for initialization
Start-Sleep -Seconds 20

# Verify containers are running
docker ps

# You should see:
# lemap_postgres
# lemap_redis
```

### Step 5: Initialize Database

```powershell
# Method 1: Using Get-Content (recommended)
Get-Content init.sql | docker exec -i lemap_postgres psql -U lemap -d lemapdb

# Method 2: If above fails
docker cp init.sql lemap_postgres:/tmp/init.sql
docker exec lemap_postgres psql -U lemap -d lemapdb -f /tmp/init.sql

# Verify tables created
docker exec lemap_postgres psql -U lemap -d lemapdb -c "\dt"
```

Expected output:
```
        List of relations
 Schema | Name  | Type  | Owner 
--------+-------+-------+-------
 public | alert | table | lemap
 public | event | table | lemap
```

### Step 6: Install Python Dependencies (Without Virtual Environment)

**If you got the venv permission error, just install directly:**

```powershell
# Install Gateway dependencies
cd gateway
pip install -r requirements.txt
cd ..

# Install Processor dependencies
cd processor
pip install -r requirements.txt
cd ..

# Install API dependencies
cd api
pip install -r requirements.txt
cd ..
```

**Optional: If you want to try venv again:**

```powershell
# Close ALL Python terminals first
# Then:
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Then install dependencies as above
```

### Step 7: Install Dashboard Dependencies

```powershell
cd HACKATHON
npm install
cd ..
```

---

## 🎮 Running the System

You need to open **5 separate PowerShell windows**.

### Terminal 1: Gateway API (Port 8000)

```powershell
cd gateway
python main.py
```

✅ Should show:
```
🚀 LEMAP Event Gateway
📡 Available Endpoints:
   POST /event        - Submit new event (requires API key)
🌐 Server: http://localhost:8000
```

### Terminal 2: Dashboard API (Port 8001)

```powershell
cd api
python main.py
```

✅ Should show:
```
🚀 LEMAP Dashboard API
📡 Available Endpoints:
   GET  /events       - Get all events
   GET  /alerts       - Get all alerts
   GET  /hub-status   - Get hub health status
🌐 Server: http://localhost:8001
```

### Terminal 3: Event Processor

```powershell
cd processor
python processor.py
```

✅ Should show:
```
🚀 LEMAP Event Processor Started Successfully
⚙️  Spike Threshold: 3 events
⏱️  Check Interval: 30 seconds
```

### Terminal 4: Event Simulator

```powershell
cd processor
python simulator.py
```

✅ Should show:
```
🎲 LEMAP Event Simulator Started
📊 Mode: normal
```

### Terminal 5: React Dashboard

```powershell
cd HACKATHON
npm run dev
```

✅ Should show:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## 📡 API Endpoints

### Gateway API (Port 8000)

#### `POST /event`
Submit a new logistics event.

**Headers:**
```
X-API-Key: lemap-secret-key-2024
Content-Type: application/json
```

**Request Body:**
```json
{
  "event_type": "ORDER_DELAYED",
  "hub": "Delhi",
  "description": "Traffic delay of 40 minutes"
}
```

**Valid Event Types:**
- `ORDER_DELAYED`
- `DELIVERY_FAILED`
- `INVENTORY_LOW`
- `VEHICLE_BREAKDOWN`
- `ROUTE_BLOCKED`
- `HUB_OVERLOAD`

**Valid Hubs:**
- `Delhi`
- `Mumbai`
- `Bangalore`
- `Chennai`
- `Hyderabad`

**Response:**
```json
{
  "status": "ok",
  "message": "Event recorded successfully",
  "event_id": 123,
  "timestamp": "2026-01-08T23:45:12"
}
```

---

### Dashboard API (Port 8001)

#### `GET /events`
Get all events with optional filtering.

**Query Parameters:**
- `hub` (optional): Filter by hub name (e.g., `Delhi`)
- `limit` (optional): Maximum number of events (default: 100)

**Examples:**
```powershell
# Get all events
Invoke-WebRequest http://localhost:8001/events

# Get events from Delhi only
Invoke-WebRequest "http://localhost:8001/events?hub=Delhi"

# Get last 50 events
Invoke-WebRequest "http://localhost:8001/events?limit=50"

# Get last 50 events from Mumbai
Invoke-WebRequest "http://localhost:8001/events?hub=Mumbai&limit=50"
```

**Response:**
```json
[
  {
    "id": 123,
    "event_type": "ORDER_DELAYED",
    "hub": "Delhi",
    "description": "Traffic delay",
    "timestamp": "2026-01-08T23:45:12"
  }
]
```

---

#### `GET /alerts`
Get all alerts with optional filtering.

**Query Parameters:**
- `hub` (optional): Filter by hub name (e.g., `Delhi`)
- `limit` (optional): Maximum number of alerts (default: 100)

**Examples:**
```powershell
# Get all alerts
Invoke-WebRequest http://localhost:8001/alerts

# Get alerts from Delhi only
Invoke-WebRequest "http://localhost:8001/alerts?hub=Delhi"

# Get last 20 alerts
Invoke-WebRequest "http://localhost:8001/alerts?limit=20"
```

**Response:**
```json
[
  {
    "id": 5,
    "hub": "Delhi",
    "event_type": "ORDER_DELAYED",
    "message": "⚠️ Spike detected: 5 ORDER_DELAYED events at Delhi",
    "timestamp": "2026-01-08T23:50:00"
  }
]
```

---

#### `GET /hub-status`
Get health status for all hubs.

**Example:**
```powershell
Invoke-WebRequest http://localhost:8001/hub-status
```

**Response:**
```json
{
  "Delhi": "red",
  "Mumbai": "green",
  "Bangalore": "green",
  "Chennai": "green",
  "Hyderabad": "green"
}
```

- `"green"` = Hub is operational
- `"red"` = Hub has active alerts (spike detected)

---

## 🧪 Testing

### Test 1: Submit Event to Gateway

```powershell
$headers = @{
    "X-API-Key" = "lemap-secret-key-2024"
    "Content-Type" = "application/json"
}

$body = @{
    event_type = "ORDER_DELAYED"
    hub = "Delhi"
    description = "Test from Windows"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/event -Method POST -Headers $headers -Body $body
```

Expected: `{"status":"ok","message":"Event recorded successfully"}`

---

### Test 2: Get Events

```powershell
# All events
Invoke-WebRequest http://localhost:8001/events | ConvertFrom-Json

# Events from specific hub
Invoke-WebRequest "http://localhost:8001/events?hub=Delhi" | ConvertFrom-Json
```

---

### Test 3: Get Alerts

```powershell
# All alerts
Invoke-WebRequest http://localhost:8001/alerts | ConvertFrom-Json

# Alerts from specific hub
Invoke-WebRequest "http://localhost:8001/alerts?hub=Mumbai" | ConvertFrom-Json
```

---

### Test 4: Get Hub Status

```powershell
Invoke-WebRequest http://localhost:8001/hub-status | ConvertFrom-Json
```

---

### Test 5: Generate Spike (for alert testing)

```powershell
# Send 5 similar events to trigger alert
$headers = @{
    "X-API-Key" = "lemap-secret-key-2024"
    "Content-Type" = "application/json"
}

$body = @{
    event_type = "ORDER_DELAYED"
    hub = "Delhi"
    description = "Spike test"
} | ConvertTo-Json

# Send 5 events
1..5 | ForEach-Object {
    Write-Host "Sending event $_..."
    Invoke-WebRequest -Uri http://localhost:8000/event -Method POST -Headers $headers -Body $body
    Start-Sleep -Seconds 2
}

# Wait 30 seconds for processor to detect spike
Write-Host "Waiting 30 seconds for processor..."
Start-Sleep -Seconds 30

# Check alerts
Write-Host "Checking alerts..."
Invoke-WebRequest http://localhost:8001/alerts | ConvertFrom-Json
```

---

### Test 6: Check Database Directly

```powershell
# View events in database
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT * FROM event ORDER BY timestamp DESC LIMIT 10;"

# View alerts in database
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT * FROM alert ORDER BY timestamp DESC LIMIT 10;"

# Count events by hub
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT hub, COUNT(*) FROM event GROUP BY hub;"

# Count alerts by hub
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT hub, COUNT(*) FROM alert GROUP BY hub;"
```

---

### Test 7: Access Dashboard

Open browser: **http://localhost:5173**

Your dashboard should connect to these 3 endpoints:
- ✅ `GET /events` - Display all events
- ✅ `GET /alerts` - Display all alerts  
- ✅ `GET /hub-status` - Show red/green hub status

---

## 🐛 Troubleshooting

### Issue: "Permission denied" creating venv

**Solution:**

```powershell
# Option 1: Delete and recreate
Remove-Item -Recurse -Force .venv
python -m venv .venv

# Option 2: Skip venv entirely (easier)
# Just install packages directly without venv
cd gateway
pip install -r requirements.txt
cd ..

cd processor  
pip install -r requirements.txt
cd ..

cd api
pip install -r requirements.txt
cd ..
```

---

### Issue: "Docker is not running"

**Solution:**
1. Open Docker Desktop
2. Wait for whale icon to show in system tray
3. Try again

---

### Issue: "Port 5432 already in use"

**Solution:**

```powershell
# Check what's using the port
Get-NetTCPConnection -LocalPort 5432

# If PostgreSQL is installed locally, stop it:
Stop-Service postgresql-x64-*

# Or use a different port in docker-compose.yml:
# Change ports to: "5433:5432"
# Then update all .env files: DB_PORT=5433
```

---

### Issue: "Password authentication failed"

**Solution:**

```powershell
# Complete reset
docker-compose down -v
docker volume prune -f
docker-compose up -d
Start-Sleep -Seconds 20

# Reinitialize database
Get-Content init.sql | docker exec -i lemap_postgres psql -U lemap -d lemapdb
```

---

### Issue: "Module not found" (Python)

**Solution:**

```powershell
# Make sure you're in the project root
# Then reinstall dependencies

cd gateway
pip install -r requirements.txt
cd ..

cd processor
pip install -r requirements.txt
cd ..

cd api
pip install -r requirements.txt
cd ..
```

---

### Issue: "Dashboard shows 'Cannot connect to API'"

**Solution:**

1. **Check API is running:**
   ```powershell
   Invoke-WebRequest http://localhost:8001/events
   ```

2. **Check HACKATHON/.env file:**
   ```powershell
   Get-Content HACKATHON\.env
   ```
   Should show: `VITE_API_BASE=http://localhost:8001`

3. **Restart dashboard:**
   ```powershell
   cd HACKATHON
   npm run dev
   ```

4. **Check browser console** (F12) for errors

---

### Issue: "npm: command not found"

**Solution:**

```powershell
# Install Node.js from https://nodejs.org/
# Restart PowerShell after installation
# Verify:
node --version
npm --version
```

---

### Issue: "No alerts generated"

**Solution:**

The processor needs **3 or more similar events** (same type + same hub) within 10 minutes to trigger an alert.

```powershell
# Generate spike manually
$headers = @{"X-API-Key"="lemap-secret-key-2024"; "Content-Type"="application/json"}
$body = @{event_type="ORDER_DELAYED"; hub="Delhi"; description="Spike test"} | ConvertTo-Json

# Send 5 events
1..5 | ForEach-Object {
    Invoke-WebRequest -Uri http://localhost:8000/event -Method POST -Headers $headers -Body $body
    Start-Sleep -Seconds 2
}

# Wait 30 seconds for processor
Start-Sleep -Seconds 30

# Check alerts
Invoke-WebRequest http://localhost:8001/alerts | ConvertFrom-Json
```

---

## 📊 Quick Commands Reference

```powershell
# ========================================
# Docker Commands
# ========================================

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Complete reset (deletes all data)
docker-compose down -v
docker volume prune -f
docker-compose up -d
Start-Sleep -Seconds 20

# ========================================
# Database Commands
# ========================================

# View recent events
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT * FROM event ORDER BY timestamp DESC LIMIT 10;"

# View recent alerts
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT * FROM alert ORDER BY timestamp DESC LIMIT 10;"

# Count events
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT COUNT(*) FROM event;"

# Events by hub
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT hub, COUNT(*) FROM event GROUP BY hub;"

# Clear all data
docker exec lemap_postgres psql -U lemap -d lemapdb -c "TRUNCATE event, alert RESTART IDENTITY;"

# ========================================
# API Testing
# ========================================

# Submit event
$headers = @{"X-API-Key"="lemap-secret-key-2024"; "Content-Type"="application/json"}
$body = @{event_type="ORDER_DELAYED"; hub="Delhi"; description="Test"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/event -Method POST -Headers $headers -Body $body

# Get all events
Invoke-WebRequest http://localhost:8001/events | ConvertFrom-Json

# Get events from specific hub
Invoke-WebRequest "http://localhost:8001/events?hub=Delhi" | ConvertFrom-Json

# Get all alerts
Invoke-WebRequest http://localhost:8001/alerts | ConvertFrom-Json

# Get hub status
Invoke-WebRequest http://localhost:8001/hub-status | ConvertFrom-Json
```

---

## 📁 Project Structure

```
New folder/                 (Your project root)
│
├── docker-compose.yml      # Infrastructure
├── init.sql                # Database schema
├── README_WINDOWS.md       # This file
│
├── gateway/                # Event Ingestion (Port 8000)
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── processor/              # Spike Detection
│   ├── processor.py
│   ├── simulator.py
│   ├── requirements.txt
│   └── .env
│
├── api/                    # Dashboard Backend (Port 8001)
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
└── HACKATHON/              # Frontend
    ├── dashboard/          # Your React app (Port 5173)
    │   └── src/
    ├── package.json
    └── .env
```

---

## 🚀 Quick Start Summary

```powershell
# 1. Start Docker
docker-compose up -d
Start-Sleep -Seconds 20

# 2. Initialize database
Get-Content init.sql | docker exec -i lemap_postgres psql -U lemap -d lemapdb

# 3. Install Python packages (no venv needed)
cd gateway; pip install -r requirements.txt; cd ..
cd processor; pip install -r requirements.txt; cd ..
cd api; pip install -r requirements.txt; cd ..

# 4. Install Node packages
cd HACKATHON; npm install; cd ..

# 5. Start services (5 separate PowerShell windows)
# Window 1: cd gateway; python main.py
# Window 2: cd api; python main.py
# Window 3: cd processor; python processor.py
# Window 4: cd processor; python simulator.py
# Window 5: cd HACKATHON; npm run dev

# 6. Open browser
# http://localhost:5173
```

---

## 🎯 Dashboard Integration

Your dashboard in `HACKATHON/dashboard/` should call these endpoints:

```javascript
// Get all events
fetch('http://localhost:8001/events')
  .then(res => res.json())
  .then(events => console.log(events));

// Get events from specific hub
fetch('http://localhost:8001/events?hub=Delhi')
  .then(res => res.json())
  .then(events => console.log(events));

// Get all alerts
fetch('http://localhost:8001/alerts')
  .then(res => res.json())
  .then(alerts => console.log(alerts));

// Get hub status
fetch('http://localhost:8001/hub-status')
  .then(res => res.json())
  .then(status => console.log(status));
  // Returns: {"Delhi": "red", "Mumbai": "green", ...}
```

---

**Built for Windows • Optimized for Hackathons • Production-Ready Architecture**

🎉 Happy Hacking!
