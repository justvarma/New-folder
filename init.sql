-- Drop tables if they exist
DROP TABLE IF EXISTS alert CASCADE;
DROP TABLE IF EXISTS event CASCADE;

-- Events table
CREATE TABLE event (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    hub VARCHAR(50) NOT NULL,
    description TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Alerts table
CREATE TABLE alert (
    id SERIAL PRIMARY KEY,
    hub VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_event_hub ON event(hub);
CREATE INDEX idx_event_timestamp ON event(timestamp DESC);
CREATE INDEX idx_alert_hub ON alert(hub);
CREATE INDEX idx_alert_timestamp ON alert(timestamp DESC);