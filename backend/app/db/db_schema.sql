-- Enable PostGIS extension for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. USERS: Extended with Roles and Status
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'citizen', -- 'admin', 'ops', 'responder', 'citizen'
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'inactive', 'on_duty'
    last_location GEOMETRY(Point, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. INCIDENTS: The core of the system
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    reporter_id INTEGER REFERENCES users(id),
    title VARCHAR(255),
    description TEXT,
    incident_type VARCHAR(50), -- 'fire', 'flood', 'earthquake', 'accident', etc.
    location GEOMETRY(Point, 4326) NOT NULL,
    photo_url VARCHAR(255),
    
    -- AI Verification & Intelligence
    ai_verified BOOLEAN DEFAULT FALSE,
    ai_confidence FLOAT, -- 0.0 to 1.0
    predicted_severity VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    actual_severity VARCHAR(20),    -- confirmed by authorities
    
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'verified', 'dispatched', 'active', 'resolved', 'fake'
    weather_snapshot JSONB, -- Store weather conditions at time of report
    
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- 3. RESOURCES: Equipment and Teams
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL, -- 'ambulance', 'fire_truck', 'police_car', 'drone', 'rescue_boat'
    status VARCHAR(20) DEFAULT 'available', -- 'available', 'busy', 'maintenance', 'deployed'
    current_location GEOMETRY(Point, 4326),
    capacity INTEGER DEFAULT 1,
    team_lead_id INTEGER REFERENCES users(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. ALLOCATIONS: Linking Resources to Incidents (Smart Resource Allocation AI)
CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE CASCADE,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    allocated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    dispatched_at TIMESTAMP WITH TIME ZONE,
    arrived_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'assigned' -- 'assigned', 'en_route', 'on_site', 'completed'
);

-- 5. DISASTER PREDICTIONS: For the Prediction Engine
CREATE TABLE disaster_predictions (
    id SERIAL PRIMARY KEY,
    location GEOMETRY(Point, 4326) NOT NULL,
    disaster_type VARCHAR(50) NOT NULL,
    probability FLOAT NOT NULL, -- 0.0 to 1.0
    alert_level VARCHAR(20),    -- 'green', 'yellow', 'orange', 'red'
    data_sources JSONB,         -- store references to weather/sensor data used
    predicted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- 6. ANALYTICS: Response Time & Performance Metrics
CREATE TABLE analytics_metrics (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER REFERENCES incidents(id),
    resource_id INTEGER REFERENCES resources(id),
    
    response_time_seconds INTEGER, -- Time from report to arrival
    resolution_time_seconds INTEGER, -- Time from report to resolved
    resource_utilization_score FLOAT, -- Efficiency score
    
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. COMMUNICATION: Team Chat & Broadcasts
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER REFERENCES incidents(id),
    sender_id INTEGER REFERENCES users(id),
    message_text TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'chat', -- 'chat', 'broadcast', 'command'
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- SPATIAL INDEXES for fast Geo-queries
CREATE INDEX idx_users_location ON users USING GIST (last_location);
CREATE INDEX idx_incidents_location ON incidents USING GIST (location);
CREATE INDEX idx_resources_location ON resources USING GIST (current_location);
CREATE INDEX idx_predictions_location ON disaster_predictions USING GIST (location);
