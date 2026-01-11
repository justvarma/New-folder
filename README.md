# 🪟 LEMAP - Windows Setup Guide

**Real-time Logistics Event Monitoring & Alerting Platform for Windows**

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the System](#running-the-system)
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

### Step 6: Install Python Dependencies

```powershell
# Create and activate virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

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
cd HACKATHON
npm install
cd ..
```

---

## 🎮 Running the System

You need to open **5 separate PowerShell windows**.

### Terminal 1: Gateway API

```powershell
# Activate venv if you created one
.\.venv\Scripts\Activate.ps1

cd gateway
python main.py
```

✅ Should show:
```
🚀 Starting LEMAP Event Gateway on http://localhost:8000
```

### Terminal 2: Dashboard API

```powershell
# Activate venv if you created one
.\.venv\Scripts\Activate.ps1

cd api
python main.py
```

✅ Should show:
```
🚀 Starting LEMAP Dashboard API on http://localhost:8001
```

### Terminal 3: Event Processor

```powershell
# Activate venv if you created one
.\.venv\Scripts\Activate.ps1

cd processor
python processor.py
```

✅ Should show:
```
🚀 LEMAP Event Processor Started Successfully
```

### Terminal 4: Event Simulator

```powershell
# Activate venv if you created one
.\.venv\Scripts\Activate.ps1

cd processor
python simulator.py
```

✅ Should show:
```
🎲 LEMAP Event Simulator Started
```

### Terminal 5: React Dashboard

```powershell
cd HACKATHON
npm run dev
```

✅ Should show:
```
Local: http://localhost:5173/
```

---

## 🧪 Testing

### Test 1: Health Checks

```powershell
# Test Gateway
Invoke-WebRequest http://localhost:8000/health | Select-Object -ExpandProperty Content

# Test API
Invoke-WebRequest http://localhost:8001/health | Select-Object -ExpandProperty Content
```

Expected: `{"gateway":"ok","postgres":"ok","redis":"ok"}`

### Test 2: Submit Test Event

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

### Test 3: View Data

```powershell
# Get events
Invoke-WebRequest http://localhost:8001/events | Select-Object -ExpandProperty Content

# Get alerts
Invoke-WebRequest http://localhost:8001/alerts | Select-Object -ExpandProperty Content

# Get hub status
Invoke-WebRequest http://localhost:8001/hub-status | Select-Object -ExpandProperty Content
```

### Test 4: Access Dashboard

Open browser: **http://localhost:5173**

You should see:
- ✅ Hub filter buttons (All Hubs, Delhi, Mumbai, etc.)
- ✅ Hub status cards with red/green indicators
- ✅ Live events feed
- ✅ Alerts feed
- ✅ Statistics

---

## 🐛 Troubleshooting

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
ports:
  - "5433:5432"  # Then update .env files to use 5433
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

### Issue: "Module not found"

**Solution:**

```powershell
# Reinstall dependencies
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

1. Check API is running: `Invoke-WebRequest http://localhost:8001/health`
2. Check CORS in `api/main.py`: Should have `allow_origins=["*"]`
3. Check `HACKATHON/.env`: Should have `VITE_API_BASE=http://localhost:8001`
4. Restart dashboard: `npm run dev`

---

### Issue: "No alerts generated"

**Solution:**

The processor needs 3+ similar events to trigger an alert.

```powershell
# Generate spike manually
$headers = @{"X-API-Key"="lemap-secret-key-2024"; "Content-Type"="application/json"}
$body = @{event_type="ORDER_DELAYED"; hub="Delhi"; description="Spike test"} | ConvertTo-Json

# Send 5 events quickly
1..5 | ForEach-Object {
    Invoke-WebRequest -Uri http://localhost:8000/event -Method POST -Headers $headers -Body $body
    Start-Sleep -Seconds 2
}

# Wait 30 seconds for processor
Start-Sleep -Seconds 30

# Check alerts
Invoke-WebRequest http://localhost:8001/alerts | Select-Object -ExpandProperty Content
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

# Complete reset
docker-compose down -v
docker volume prune -f
docker-compose up -d

# ========================================
# Database Commands
# ========================================

# Connect to PostgreSQL
docker exec -it lemap_postgres psql -U lemap -d lemapdb

# View events
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT * FROM event ORDER BY timestamp DESC LIMIT 10;"

# View alerts
docker exec lemap_postgres psql -U lemap -d lemapdb -c "SELECT * FROM alert ORDER BY timestamp DESC LIMIT 10;"

# Clear all data
docker exec lemap_postgres psql -U lemap -d lemapdb -c "TRUNCATE event, alert RESTART IDENTITY;"

# ========================================
# Redis Commands
# ========================================

# Connect to Redis
docker exec -it lemap_redis redis-cli

# View all keys
docker exec lemap_redis redis-cli KEYS "*"

# View event counters
docker exec lemap_redis redis-cli KEYS "event_count:*"

# View hub status
docker exec lemap_redis redis-cli GET "hub_status:Delhi"

# ========================================
# API Testing
# ========================================

# Health checks
Invoke-WebRequest http://localhost:8000/health
Invoke-WebRequest http://localhost:8001/health

# Submit event
$headers = @{"X-API-Key"="lemap-secret-key-2024"; "Content-Type"="application/json"}
$body = @{event_type="ORDER_DELAYED"; hub="Delhi"; description="Test"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/event -Method POST -Headers $headers -Body $body

# Get data
Invoke-WebRequest http://localhost:8001/events
Invoke-WebRequest http://localhost:8001/alerts
Invoke-WebRequest http://localhost:8001/hub-status
Invoke-WebRequest http://localhost:8001/stats
```

---

## 📁 Project Structure

```
lemap-project/
│
├── docker-compose.yml          # Infrastructure
├── init.sql                    # Database schema
├── README_WINDOWS.md           # This file
│
├── gateway/                    # Event Ingestion (Port 8000)
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── processor/                  # Spike Detection
│   ├── processor.py            # Worker
│   ├── simulator.py            # Event generator
│   ├── requirements.txt
│   └── .env
│
├── api/                        # Dashboard Backend (Port 8001)
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
└── HACKATHON/                  # Frontend (Port 5173)
    ├── dashboard/
    ├── package.json
    └── .env
```

---

## 🎯 Dashboard Features

### Hub Status Cards
- Click any hub card to filter events and alerts for that hub
- Green indicator = Hub operational
- Red indicator = Hub in alert state

### Event Feed
- Shows all recent logistics events
- Color-coded by event type
- Filters by selected hub

### Alert Feed
- Shows generated alerts from spike detection
- Displays hub name and event type
- Auto-refreshes every 5 seconds

### Statistics
- Total events count
- Active alerts count
- Number of hubs in alert state

---

## 🔐 Security Notes

**For Development:**
- API key is hardcoded: `lemap-secret-key-2024`
- CORS allows all origins: `allow_origins=["*"]`
- Database uses simple password

**For Production:**
- Change API key to strong random string
- Restrict CORS to specific domains
- Use environment variables for secrets
- Enable SSL/TLS
- Use strong database password

---

## 🚀 Quick Start Summary

```powershell
# 1. Start Docker
docker-compose up -d
Start-Sleep -Seconds 20

# 2. Initialize database
Get-Content init.sql | docker exec -i lemap_postgres psql -U lemap -d lemapdb

# 3. Open 5 PowerShell windows and run:
# Terminal 1: cd gateway; python main.py
# Terminal 2: cd api; python main.py
# Terminal 3: cd processor; python processor.py
# Terminal 4: cd processor; python simulator.py
# Terminal 5: cd HACKATHON; npm run dev

# 4. Open browser
# http://localhost:5173
```

---

## 📞 Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section
2. View Docker logs: `docker-compose logs`
3. Check service health: `Invoke-WebRequest http://localhost:8000/health`
4. Verify containers running: `docker ps`

---

## 🎓 Learning Resources

- **Docker Desktop**: https://docs.docker.com/desktop/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Redis**: https://redis.io/docs/

---

**Built for Windows • Optimized for Hackathons • Production-Ready Architecture**

🎉 Happy Hacking!
