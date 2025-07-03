-- Habilitar la extensión PostGIS (si no está ya habilitada)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Crear tabla users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_employee BOOLEAN NOT NULL DEFAULT FALSE
);

-- Crear tabla ports
CREATE TABLE IF NOT EXISTS ports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    country VARCHAR(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);



CREATE TABLE hindcast_points (
    id SERIAL PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    url VARCHAR NOT NULL,
    models JSON NULL
);


INSERT INTO hindcast_points (latitude, longitude, url, models)
VALUES (
    54.544587,
    7.0,
    'https://marine-api.open-meteo.com/v1/marine',
    '["ERA5-OCEAN", "METEOFRANCE WAVE"]'::json
);

CREATE TABLE downloaded_data (
    id SERIAL PRIMARY KEY,
    downloaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    point_id INTEGER NOT NULL,
    data JSONB NOT NULL,
    CONSTRAINT fk_point FOREIGN KEY (point_id) REFERENCES hindcast_points(id) ON DELETE CASCADE
);

CREATE INDEX idx_latest_download_per_point ON downloaded_data (point_id, downloaded_at DESC);

CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    forecast_system_id INTEGER NOT NULL REFERENCES forecast_systems(id) ON DELETE CASCADE,
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);




CREATE TABLE IF NOT EXISTS forecast_systems (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE, -- Añadido UNIQUE para el nombre
    description TEXT, -- Añadida una descripción opcional
    
    -- Claves foráneas con relación 1:1 (nullable si no todos los sistemas tienen uno)
    contract_id INTEGER UNIQUE, -- UNIQUE para asegurar la relación 1:1 desde este lado
    port_id INTEGER UNIQUE,     -- UNIQUE para asegurar la relación 1:1 desde este lado
    hindcast_point_id INTEGER UNIQUE, -- UNIQUE para asegurar la relación 1:1 desde este lado

    -- Restricciones de clave foránea (asegúrate de que estas tablas existan)
    CONSTRAINT fk_contract
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id)
        ON DELETE SET NULL, -- O CASCADE, o RESTRICT, según tu lógica
    CONSTRAINT fk_port
        FOREIGN KEY (port_id)
        REFERENCES ports(id)
        ON DELETE SET NULL,
    CONSTRAINT fk_hindcast_point
        FOREIGN KEY (hindcast_point_id)
        REFERENCES hindcast_points(id)
        ON DELETE SET NULL
);

-- Crear tabla forecast_zones
CREATE TABLE IF NOT EXISTS forecast_zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    forecast_system_id INTEGER NOT NULL REFERENCES forecast_systems(id) ON DELETE CASCADE, 
    -- 'geom' puede almacenar cualquier tipo de geometría (Point, Polygon, etc.) en WGS84
    geom GEOMETRY(Geometry, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_forecast_zones_geom ON forecast_zones USING GIST (geom);

INSERT INTO forecast_systems (name) VALUES ('Sistema de Previsión A');
INSERT INTO forecast_systems (name) VALUES ('Sistema de Previsión B');







-- Tabla intermedia entre users y contracts
CREATE TABLE  IF NOT EXISTS user_contracts (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, contract_id)
);




-- Insertar usuario admin
INSERT INTO users (username, email, hashed_password, is_admin, is_employee)
VALUES ('admin', 'admin@example.com', '$2b$12$vBwE85h4womp.Ye8NoJOJe9LCWnwURGiFJSFI2VhhrnXIUDPdqn32', TRUE, TRUE)
ON CONFLICT DO NOTHING;

-- Insertar usuario normal
INSERT INTO users (username, email, hashed_password, is_admin, is_employee)
VALUES ('user1', 'user1@example.com', '$2b$12$XSI9yM9H7KTVU5j9AUKIqOBIRGc\r6NXrS5AEySHnx\XiWQ7HNONy', FALSE, TRUE)
ON CONFLICT DO NOTHING;


-- Insertar usuario normal
INSERT INTO users (username, email, hashed_password, is_admin, is_employee)
VALUES ('mvigo', 'mvigo@example.com', '$2b$12$vBwE85h4womp.Ye8NoJOJe9LCWnwURGiFJSFI2VhhrnXIUDPdqn32', FALSE, FALSE)
ON CONFLICT DO NOTHING;


-- Insertar puertos de ejemplo
INSERT INTO ports (name, country, latitude, longitude) VALUES
('Puerto de Valencia', 'España', 39.4561, -0.3389),
('Puerto de Róterdam', 'Países Bajos', 51.9225, 4.4792),
('Puerto de Hamburgo', 'Alemania', 53.5511, 9.9937)
ON CONFLICT DO NOTHING;



INSERT INTO contracts (name, forecast_system_id, start_date, end_date, active)
VALUES 
  ('Contrato A', 1, '2025-06-01', NULL, true),
  ('Contrato B', 1, '2025-07-01', '2025-12-31', true),
  ('Contrato C', 2, '2025-01-15', NULL, false);


  INSERT INTO user_contracts (user_id, contract_id)
VALUES 
  (1, 1),
  (1, 2),
  (2, 2),
  (3, 3);