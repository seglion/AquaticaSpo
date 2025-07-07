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
    name VARCHAR(255) NOT NULL ,
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
    -- ELIMINAMOS forecast_system_id de aquí, ya que la FK va en forecast_systems
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);


-- 3. Create forecast_systems (Ahora con contract_id y su FK única)
CREATE TABLE IF NOT EXISTS forecast_systems (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    -- Añadimos la columna 'description' si la quieres mantener en la DB

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
    CONSTRAINT fk_contract_on_forecast_system -- Nombre de la FK más descriptivo
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id)
        ON DELETE SET NULL -- O CASCADE, o RESTRICT, según tu lógica de negocio
);


CREATE TABLE IF NOT EXISTS forecast_system_results (
    id SERIAL PRIMARY KEY,
    forecast_zone_id INTEGER NOT NULL, -- FK a la zona de previsión
    execution_date TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Fecha y hora de cuándo se ejecutó el modelo
    result_data JSONB NOT NULL, -- Aquí se guardará el JSON con los datos de previsión
    
    CONSTRAINT fk_forecast_zone
        FOREIGN KEY (forecast_zone_id)
        REFERENCES forecast_zones(id)
        ON DELETE CASCADE -- Si se elimina la zona, se eliminan sus resultados
);

-- Índices para mejorar el rendimiento de las consultas
CREATE INDEX IF NOT EXISTS idx_forecast_system_results_zone_id ON forecast_system_results (forecast_zone_id);
CREATE INDEX IF NOT EXISTS idx_forecast_system_results_execution_date ON forecast_system_results (execution_date DESC);






-- 4. Create user_contracts (depends on users and contracts)
CREATE TABLE IF NOT EXISTS user_contracts (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, contract_id)
);

-- 5. Create forecast_zones (depends on forecast_systems)
CREATE TABLE IF NOT EXISTS forecast_zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    forecast_system_id INTEGER NOT NULL REFERENCES forecast_systems(id) ON DELETE CASCADE,
    geom GEOMETRY(Geometry, 4326) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_forecast_zones_geom ON forecast_zones USING GIST (geom);


---
-- DATA INSERTION
---

-- TRUNCATE TABLES (para un estado limpio en desarrollo)
TRUNCATE TABLE user_contracts CASCADE;
TRUNCATE TABLE forecast_zones CASCADE;
TRUNCATE TABLE downloaded_data CASCADE;
TRUNCATE TABLE forecast_systems CASCADE;
TRUNCATE TABLE contracts CASCADE;
TRUNCATE TABLE ports CASCADE;
TRUNCATE TABLE hindcast_points CASCADE;
TRUNCATE TABLE users RESTART IDENTITY CASCADE; -- Siempre última y con RESTART IDENTITY

-- Insert users
INSERT INTO users (username, email, hashed_password, is_admin, is_employee)
VALUES
('admin', 'admin@example.com', '$2b$12$vBwE85h4womp.Ye8NoJOJe9LCWnwURGiFJSFI2VhhrnXIUDPdqn32', TRUE, TRUE),
('user1', 'user1@example.com', '$2b$12$XSI9yM9H7KTVU5j9AUKIqOBIRGc\r6NXrS5AEySHnx\XiWQ7HNONy', FALSE, TRUE),
('mvigo', 'mvigo@example.com', '$2b$12$vBwE85h4womp.Ye8NoJOJe9LCWnwURGiFJSFI2VhhrnXIUDPdqn32', FALSE, FALSE);


-- Insert ports
INSERT INTO ports (name, country, latitude, longitude) VALUES
('Puerto de Valencia', 'España', 39.4561, -0.3389),
('Puerto de Róterdam', 'Países Bajos', 51.9225, 4.4792),
('Puerto de Hamburgo', 'Alemania', 53.5511, 9.9937);


-- Insert hindcast_points
INSERT INTO hindcast_points (latitude, longitude, url, models)
VALUES (
    54.544587,
    7.0,
    'https://marine-api.open-meteo.com/v1/marine',
    '["ERA5-OCEAN", "METEOFRANCE WAVE"]'::json
) ;


-- Insert contracts (antes que forecast_systems, ya que forecast_systems los referencia)
INSERT INTO contracts (name, start_date, end_date, active)
VALUES
('Contrato A - Global', '2025-06-01', NULL, TRUE),
('Contrato B - Regional', '2025-07-01', '2025-12-31', TRUE),
('Contrato C - Prueba', '2025-01-15', NULL, FALSE);


-- Insert forecast systems (ahora referencian contratos por ID)
INSERT INTO forecast_systems (name, description, contract_id, port_id, hindcast_point_id) VALUES
('Sistema de Previsión A', 'Sistema global para predicciones marítimas.', 1, 1, 1), -- Asocia a Contrato A, Puerto Valencia, HindcastPoint 1
('Sistema de Previsión B', 'Sistema regional para predicciones costeras.', 2, 2, NULL), -- Asocia a Contrato B, Puerto Róterdam
('Sistema de Previsión C', 'Sistema sin contrato', NULL, NULL, NULL); -- Sin contrato asociado


-- Insert user_contracts (usa los IDs de users y contracts ya insertados)
INSERT INTO user_contracts (user_id, contract_id)
VALUES
(1, 1), -- admin tiene Contrato A
(1, 2), -- admin también tiene Contrato B
(2, 2), -- user1 tiene Contrato B
(3, 3); -- mvigo tiene Contrato C


-- Insert forecast_zones (usa los IDs de forecast_systems ya insertados)
INSERT INTO forecast_zones (name, description, forecast_system_id, geom) VALUES
('Zona Atlántica', 'Una zona de previsión para el Atlántico.', 1, ST_SetSRID(ST_GeomFromText('POLYGON((-10 40, 0 40, 0 50, -10 50, -10 40))'), 4326)),
('Zona Mediterránea', 'Una zona de previsión para el Mediterráneo.', 2, ST_SetSRID(ST_GeomFromText('POLYGON((0 30, 10 30, 10 40, 0 40, 0 30))'), 4326));