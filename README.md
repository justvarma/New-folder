# 🪟 LEMAP - Windows Setup Guide

**Real-time Logistics Event Monitoring & Alerting Platform for Windows**

> **Project Location:** `C:\Users\adity\OneDrive\Desktop\New folder\`

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

### Step 1: Navigate to Project Folder

```powershell
cd "C:\Users\adity\OneDrive\Desktop\New folder"
```

### Step 2: Verify Files Exist

```powershell
# Check if required files exist
Test-Path docker-compose.yml
Test-Path init.sql
Test-Path gateway\main.py
Test-Path processor\processor.py
Test-Path api\main.py
Test-Path HACKATHON\package.json
```

All should return `True`.

### Step 3: Create .env Files (If Not Already Created)

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

### Step 4: Start Docker Services

```powershell
# Make sure you're in the "New folder" directory
cd "C:\Users\adity\OneDrive\Desktop\New folder"

# Start Docker containers
docker-compose up -d

# Wait 20 seconds for initialization
Start-Sleep -Seconds 20

# Verify containers are running
docker ps
```

You should see:
```
lemap_postgres
lemap_redis
```

### Step 5: Initialize Database

```powershell
# Initialize database schema
Get-Content init.sql | docker exec -i lemap_postgres psql -U lemap -d lemapdb

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

### Step 6: Install Python Dependencies (Skip Virtual Environment)

Since you had venv permission issues, install directly:

```powershell
# Make sure you're in project root
cd "C:\Users\adity\OneDrive\Desktop\New folder"

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

### Step 7: Install Dashboard Dependencies

```powershell
# Install Node packages for dashboard
cd HACKATHON
npm install
cd ..
```

---

## 🎮 Running the System

You need to open **5 separate PowerShell windows**.

### Terminal 1: Gateway API (Port 8000)

```powershell
cd "C:\Users\adity\OneDrive\Desktop\New folder\gateway"
python main.py
```

✅ Should show:
```
🚀 LEMAP Event Gateway
📡 Available Endpoints:
   POST /event        - Submit new event (requires API key)
🌐 Server: http://localhost:8000
```

---

### Terminal 2: Dashboard API (Port 8001)

```powershell
cd "C:\Users\adity\OneDrive\Desktop\New folder\api"
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

---

### Terminal 3: Event Processor

```powershell
cd "C:\Users\adity\OneDrive\Desktop\New folder\processor"
python processor.py
```

✅ Should show:
```
🚀 LEMAP Event Processor Started Successfully
⚙️  Spike Threshold: 3 events
⏱️  Check Interval: 30 seconds
```

---

### Terminal 4: Event Simulator

```powershell
cd "C:\Users\adity\OneDrive\Desktop\New folder\processor"
python simulator.py
```

✅ Should show:
```
🎲 LEMAP Event Simulator Started
📊 Mode: normal
[10:30:45] ✅ [1] Delhi | ORDER_DELAYED
```

---

### Terminal 5: React Dashboard

```powershell
cd "C:\Users\adity\OneDrive\Desktop\New folder\HACKATHON\dashboard"
npm run dev
```

✅ Should show:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
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

---

### Dashboard API (Port 8001)

#### 1. `GET /events`
Get all events with optional filtering.

**Query Parameters:**
- `hub` (optional): Filter by hub name
- `limit` (optional): Max events (default: 100)

**Examples:**
```javascript
// In your dashboard code
fetch('http://localhost:8001/events')
fetch('http://localhost:8001/events?hub=Delhi')
fetch('http://localhost:8001/events?limit=50')
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

#### 2. `GET /alerts`
Get all alerts with optional filtering.

**Query Parameters:**
- `hub` (optional): Filter by hub name
- `limit` (optional): Max alerts (default: 100)

**Examples:**
```javascript
// In your dashboard code
fetch('http://localhost:8001/alerts')
fetch('http://localhost:8001/alerts?hub=Delhi')
fetch('http://localhost:8001/alerts?limit=20')
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

#### 3. `GET /hub-status`
Get health status for all hubs (red/green).

**Example:**
```javascript
// In your dashboard code
fetch('http://localhost:8001/hub-status')
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

- `"green"` = Hub operational
- `"red"` = Hub has active alerts

---

## 🧪 Testing

### Test 1: Submit Event

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

---

### Test 2: Get Events

```powershell
# All events
Invoke-WebRequest http://localhost:8001/events | ConvertFrom-Json

# Events from Delhi
Invoke-WebRequest "http://localhost:8001/events?hub=Delhi" | ConvertFrom-Json
```

---

### Test 3: Get Alerts

```powershell
# All alerts
Invoke-WebRequest http://localhost:8001/alerts | ConvertFrom-Json

# Alerts from Mumbai
Invoke-WebRequest "http://localhost:8001/alerts?hub=Mumbai" | ConvertFrom-Json
```

---

### Test 4: Get Hub Status

```powershell
Invoke-WebRequest http://localhost:8001/hub-status | ConvertFrom-Json
```

---

### Test 5: Generate Spike (Trigger Alert)

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

# Wait 30 seconds for processor
Write-Host "`nWaiting 30 seconds for processor to detect spike..."
Start-Sleep -Seconds 30

# Check alerts
Write-Host "`nChecking alerts..."
Invoke-WebRequest http://localhost:8001/alerts | ConvertFrom-Json
```

---

### Test 6: Check Database

```powershell
# View events
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT * FROM event ORDER BY timestamp DESC LIMIT 10;"

# View alerts
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT * FROM alert ORDER BY timestamp DESC LIMIT 10;"

# Count by hub
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT hub, COUNT(*) FROM event GROUP BY hub;"
```

---

### Test 7: Access Dashboard

Open browser: **http://localhost:5173**

Your dashboard should display data from the 3 API endpoints.

---

## 🐛 Troubleshooting

### Issue: "Permission denied" creating .venv

**Solution:** Skip virtual environment entirely (we did this in Step 6).

```powershell
# Just install packages directly
cd gateway
pip install -r requirements.txt
cd ..
```

---

### Issue: "Docker is not running"

**Solution:**
1. Open Docker Desktop
2. Wait for whale icon in system tray
3. Try: `docker ps`

---

### Issue: "Port 5432 already in use"

**Solution:**

```powershell
# Check what's using it
Get-NetTCPConnection -LocalPort 5432

# If local PostgreSQL, stop it
Stop-Service postgresql-x64-*
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

# Reinitialize
Get-Content init.sql | docker exec -i lemap_postgres psql -U lemap -d lemapdb
```

---

### Issue: "Module not found" (Python)

**Solution:**

```powershell
# Reinstall
cd "C:\Users\adity\OneDrive\Desktop\New folder\gateway"
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

### Issue: Dashboard can't connect to API

**Solution:**

1. **Check API is running:**
   ```powershell
   Invoke-WebRequest http://localhost:8001/events
   ```

2. **Check HACKATHON/.env:**
   ```powershell
   cd "C:\Users\adity\OneDrive\Desktop\New folder"
   Get-Content HACKATHON\.env
   ```
   Should show: `VITE_API_BASE=http://localhost:8001`

3. **Restart dashboard:**
   ```powershell
   cd HACKATHON
   npm run dev
   ```

---

### Issue: No alerts generated

**Explanation:** Processor needs 3+ similar events (same type + hub) within 10 minutes.

**Solution:** Use Test 5 above to generate a spike.

---

## 📊 Quick Commands

```powershell
# Navigate to project
cd "C:\Users\adity\OneDrive\Desktop\New folder"

# ========================================
# Docker
# ========================================

# Start
docker-compose up -d

# Stop
docker-compose down

# Reset (deletes all data)
docker-compose down -v
docker volume prune -f
docker-compose up -d

# View logs
docker-compose logs -f

# ========================================
# Database
# ========================================

# View events
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT * FROM event LIMIT 10;"

# View alerts
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT * FROM alert LIMIT 10;"

# Clear data
docker exec lemap_postgres psql -U lemap -d lemapdb -c "TRUNCATE event, alert RESTART IDENTITY;"

# ========================================
# API Testing
# ========================================

# Submit event
$h = @{"X-API-Key"="lemap-secret-key-2024"; "Content-Type"="application/json"}
$b = @{event_type="ORDER_DELAYED"; hub="Delhi"; description="Test"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/event -Method POST -Headers $h -Body $b

# Get events
Invoke-WebRequest http://localhost:8001/events

# Get alerts
Invoke-WebRequest http://localhost:8001/alerts

# Get hub status
Invoke-WebRequest http://localhost:8001/hub-status
```

---

## 📁 Your Folder Structure

```
C:\Users\adity\OneDrive\Desktop\New folder\
│
├── docker-compose.yml      # Infrastructure
├── init.sql                # Database schema
├── README_WINDOWS.md       # This file
│
├── gateway/                # Port 8000 - Event Ingestion
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
├── api/                    # Port 8001 - Dashboard Backend
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
└── HACKATHON/              # Frontend
    ├── dashboard/          # Port 5173 - Your React app
    │   └── src/
    ├── package.json
    ├── package-lock.json
    └── .env
```

---

## 🚀 Quick Start (Copy-Paste This!)

```powershell
# 1. Navigate to project
cd "C:\Users\adity\OneDrive\Desktop\New folder"

# 2. Start Docker
docker-compose up -d
Start-Sleep -Seconds 20

# 3. Initialize database
Get-Content init.sql | docker exec -i lemap_postgres psql -U lemap -d lemapdb

# 4. Install Python packages (if not done)
cd gateway; pip install -r requirements.txt; cd ..
cd processor; pip install -r requirements.txt; cd ..
cd api; pip install -r requirements.txt; cd ..

# 5. Install Node packages (if not done)
cd HACKATHON; npm install; cd ..

# 6. Open 5 PowerShell windows and run:
# Window 1: cd "C:\Users\adity\OneDrive\Desktop\New folder\gateway"; python main.py
# Window 2: cd "C:\Users\adity\OneDrive\Desktop\New folder\api"; python main.py
# Window 3: cd "C:\Users\adity\OneDrive\Desktop\New folder\processor"; python processor.py
# Window 4: cd "C:\Users\adity\OneDrive\Desktop\New folder\processor"; python simulator.py
# Window 5: cd "C:\Users\adity\OneDrive\Desktop\New folder\HACKATHON"; npm run dev

# 7. Open browser: http://localhost:5173
```

---

## 🎯 Dashboard Integration

Your dashboard in `HACKATHON/dashboard/src/` should call:

```javascript
// 1. Get all events
fetch('http://localhost:8001/events')
  .then(res => res.json())
  .then(data => {
    // Display events in your UI
    console.log('Events:', data);
  });

// 2. Get alerts
fetch('http://localhost:8001/alerts')
  .then(res => res.json())
  .then(data => {
    // Display alerts in your UI
    console.log('Alerts:', data);
  });

// 3. Get hub status (red/green)
fetch('http://localhost:8001/hub-status')
  .then(res => res.json())
  .then(data => {
    // Display hub status indicators
    console.log('Hub Status:', data);
    // e.g., {"Delhi": "red", "Mumbai": "green", ...}
  });

// 4. Filter by hub
fetch('http://localhost:8001/events?hub=Delhi')
  .then(res => res.json())
  .then(data => {
    // Display only Delhi events
  });
```

---

**Everything you need is in: `C:\Users\adity\OneDrive\Desktop\New folder\`**

🎉 Happy Hacking!
