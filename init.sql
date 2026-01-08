-- LEMAP Database Schema
-- Run this after starting PostgreSQL

-- Drop tables if they exist (for clean setup)
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

-- Indexes for performance
CREATE INDEX idx_event_hub ON event(hub);
CREATE INDEX idx_event_type ON event(event_type);
CREATE INDEX idx_event_timestamp ON event(timestamp DESC);
CREATE INDEX idx_event_hub_type ON event(hub, event_type);

CREATE INDEX idx_alert_hub ON alert(hub);
CREATE INDEX idx_alert_type ON alert(event_type);
CREATE INDEX idx_alert_timestamp ON alert(timestamp DESC);

-- Insert some sample data for testing
INSERT INTO event (event_type, hub, description) VALUES
    ('ORDER_DELAYED', 'Delhi', 'Traffic causing delays'),
    ('INVENTORY_LOW', 'Mumbai', 'Stock running low'),
    ('VEHICLE_BREAKDOWN', 'Bangalore', 'Engine failure');

-- Verify tables
SELECT 'Events table created' as status, COUNT(*) as sample_count FROM event;
SELECT 'Alerts table created' as status, COUNT(*) as sample_count FROM alert;