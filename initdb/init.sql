-- Habilitar la extensión PostGIS (si no está ya habilitada)
CREATE EXTENSION IF NOT EXISTS postgis;

---
-- TABLE CREATION
---

-- 1. Create independent tables first: users, ports, hindcast_points

-- Create table users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_employee BOOLEAN NOT NULL DEFAULT FALSE
);

-- Create table ports
CREATE TABLE IF NOT EXISTS ports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

-- Create table hindcast_points
CREATE TABLE IF NOT EXISTS hindcast_points (
    id SERIAL PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    url VARCHAR NOT NULL,
    models JSON NULL
);

-- Create table downloaded_data (depends on hindcast_points)
CREATE TABLE IF NOT EXISTS downloaded_data (
    id SERIAL PRIMARY KEY,
    downloaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    point_id INTEGER NOT NULL,
    data JSONB NOT NULL,
    CONSTRAINT fk_point FOREIGN KEY (point_id) REFERENCES hindcast_points(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_latest_download_per_point ON downloaded_data (point_id, downloaded_at DESC);

-- 2. Create contracts (debe crearse antes de forecast_systems si forecast_systems va a referenciarla)
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 3. Create forecast_systems (Ahora con contract_id y su FK única)
CREATE TABLE IF NOT EXISTS forecast_systems (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,

    -- Claves foráneas a otras entidades (port_id, hindcast_point_id)
    port_id INTEGER UNIQUE,
    hindcast_point_id INTEGER UNIQUE,

    -- Clave foránea a contracts, con UNIQUE para la relación 1:1
    contract_id INTEGER UNIQUE,

    CONSTRAINT fk_port
        FOREIGN KEY (port_id)
        REFERENCES ports(id)
        ON DELETE SET NULL,
    CONSTRAINT fk_hindcast_point
        FOREIGN KEY (hindcast_point_id)
        REFERENCES hindcast_points(id)
        ON DELETE SET NULL,
    CONSTRAINT fk_contract_on_forecast_system
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id)
        ON DELETE SET NULL
);

-- Create table forecast_zones
-- Corregido: location_geometry ahora es GEOMETRY para aceptar Point o Polygon
-- Añadido: forecast_system_id y su FK
-- Create table forecast_zones (CORRECCIÓN AQUÍ: location_geometry -> geom)
CREATE TABLE IF NOT EXISTS forecast_zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    geom GEOMETRY(Geometry, 4326) NULL, -- Cambiado de 'location_geometry' a 'geom'
    description TEXT NULL,
    dock_elevation DOUBLE PRECISION NULL,
    forecast_system_id INTEGER NOT NULL,
    CONSTRAINT fk_forecast_system_zone
        FOREIGN KEY (forecast_system_id)
        REFERENCES forecast_systems(id)
        ON DELETE CASCADE
);

-- Create table forecast_system_results
CREATE TABLE IF NOT EXISTS forecast_system_results (
    id SERIAL PRIMARY KEY,
    forecast_zone_id INTEGER NOT NULL,
    execution_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    result_data JSONB NOT NULL,
    
    CONSTRAINT fk_forecast_zone
        FOREIGN KEY (forecast_zone_id)
        REFERENCES forecast_zones(id)
        ON DELETE CASCADE
);

-- Índices para mejorar el rendimiento de las consultas
CREATE INDEX IF NOT EXISTS idx_forecast_system_results_zone_id ON forecast_system_results (forecast_zone_id);
CREATE INDEX IF NOT EXISTS idx_forecast_system_results_execution_date ON forecast_system_results (execution_date DESC);


-- NEW TABLE: user_contracts (many-to-many relationship)
CREATE TABLE IF NOT EXISTS user_contracts (
    user_id INTEGER NOT NULL,
    contract_id INTEGER NOT NULL,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, contract_id),
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_contract
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id)
        ON DELETE CASCADE
);


---
-- DATA INSERTION
---

-- Insert 5 sample users
INSERT INTO users (username, email, hashed_password, is_admin, is_employee) VALUES
('mvigo', 'mvigo@aquaticaingenieria.com', '$2b$12$EZIE4Y4L4yMTdZ/UM0kC7eK4OhN2u6sOYNWxoBA722NJztzWTbV66', TRUE, TRUE),
('modelo', 'info@aquaticaingenieria.com', '$2b$12$CkBb.Z/Y8PT2eqp0zIhNKeqev3lvKJTccnLZ5cyyqc36Yw2.BE9QC', TRUE, TRUE),
('flopezmera', 'flopezmera@aquaticaingenieria.com', '$2b$12$gFUrcnZAUbQK1nljvuU70eOGqFWugCiUJaUwas5wP9.3kuKqtpIGK', FALSE, TRUE),
('client_user_1', 'client1@example.com', '$2b$12$mhlueUedkxr1nquvEBxzIe5BuWoTHWf9AR9enb9clWbWcLtfSgnGC', FALSE, FALSE),
('guest_user', 'guest@example.com', '$2b$12$mhlueUedkxr1nquvEBxzIe5BuWoTHWf9AR9enb9clWbWcLtfSgnGC', FALSE, FALSE)
ON CONFLICT (username) DO NOTHING;

-- Cuenta de servicio dedicada del microservicio mailer (autentica sus llamadas a la API).
-- La contraseña en texto plano es la que va en MAILER_API_PASSWORD dentro de .env.
INSERT INTO users (username, email, hashed_password, is_admin, is_employee) VALUES
('mailer_service', 'mailer@aquatica.gal', '$2b$12$GHYd13D95cVdm4jNF6nIN.ZHAfR6eUrR7Tp2hUEusDOBwB2z9BX5u', TRUE, FALSE)
ON CONFLICT (username) DO NOTHING;


-- Insert 1 sample ports
INSERT INTO ports (name, country, latitude, longitude) VALUES
('Puerto de Burela', 'España',   43.657498,   -7.353101)
ON CONFLICT (id) DO NOTHING;


-- Insert 5 sample hindcast_points
INSERT INTO hindcast_points (latitude, longitude, url, models) VALUES
(43.875, -7.2083282, 'https://marine-api.open-meteo.com/v1/marine', '["meteofrance_wave,ewam,ecmwf_wam025,ncep_gfswave025,ncep_gfswave016"]')
ON CONFLICT DO NOTHING;


-- Insert 5 sample downloaded_data (dependent on hindcast_points)
INSERT INTO downloaded_data (point_id, data) VALUES
(1, '{"date": "2025-07-01T00:00:00Z", "data_type": "wave_height", "value": 2.5}'),
(1, '{"date": "2025-07-01T01:00:00Z", "data_type": "wind_speed", "value": 15.2}'),
(1, '{"date": "2025-07-01T02:00:00Z", "data_type": "current_dir", "value": 90}'),
(1, '{"date": "2025-07-01T03:00:00Z", "data_type": "temperature", "value": 18.7}'),
(1, '{"date": "2025-07-01T04:00:00Z", "data_type": "salinity", "value": 35.1}')
ON CONFLICT (id) DO NOTHING;


-- Insert 5 sample contracts
INSERT INTO contracts (name, start_date, end_date, active) VALUES
('Burela MarcorXove', '2025-08-01', NULL, TRUE)
ON CONFLICT (id) DO NOTHING;


-- Insert 5 sample forecast_systems (dependent on ports, hindcast_points, contracts)
INSERT INTO forecast_systems (name, port_id, hindcast_point_id, contract_id) VALUES
('Sistema Previsión Burela',  1, 1, 1)
ON CONFLICT (name) DO NOTHING;


-- Insert 5 sample forecast_zones
-- Corregido: Ahora incluye forecast_system_id. Los IDs 1-5 son los de los sistemas de previsión.
-- location_geometry puede ser POINT o POLYGON.
INSERT INTO forecast_zones (name, geom,description, forecast_system_id) VALUES

('Punto Puerto Exterior 1', ST_SetSRID(ST_GeomFromText('POINT ( -7.349343 43.657969)'), 4326), 'Punto de control en el puerto de Burela.', 1),
('Punto Puerto Exterior 2', ST_SetSRID(ST_GeomFromText('POINT ( -7.347691 43.657606)'), 4326), 'Punto de control en el puerto de Burela.', 1),
('Punto Puerto Exterior 3', ST_SetSRID(ST_GeomFromText('POINT ( -7.344322 43.656283)'), 4326), 'Punto de control en el puerto de Burela.', 1)

-- ('Bahía de Algeciras', ST_SetSRID(ST_GeomFromText('POLYGON ((-5.5 36, -5.4 36, -5.4 36.1, -5.5 36.1, -5.5 36))'), 4326), 'Zona de previsión de alta resolución para la Bahía de Algeciras.', 1),
-- ('Punto Fondeo Ría', ST_SetSRID(ST_GeomFromText('POINT (-8.8 42.15)'), 4326), 'Punto de fondeo en la ría de Pontevedra.', 1),
-- ('Mediterráneo Norte', ST_SetSRID(ST_GeomFromText('POLYGON ((1 40, 2 40, 2 41, 1 41, 1 40))'), 4326), 'Zona para el levante español.', 2)
ON CONFLICT (name) DO NOTHING;


-- Insert 5 sample forecast_system_results
INSERT INTO forecast_system_results (forecast_zone_id, execution_date, result_data) VALUES
(1, '2025-07-07 00:00:00+02', '{"Hs": 1.8, "Tp": 6.2, "Dir": 270}')
ON CONFLICT (id) DO NOTHING;

-- Insert 5 sample user_contracts
INSERT INTO user_contracts (user_id, contract_id) VALUES
(4, 1)
ON CONFLICT (user_id, contract_id) DO NOTHING;