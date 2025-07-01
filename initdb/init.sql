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

-- Insertar usuario admin
INSERT INTO users (username, email, hashed_password, is_admin, is_employee)
VALUES ('admin', 'admin@example.com', '$2b$12$vBwE85h4womp.Ye8NoJOJe9LCWnwURGiFJSFI2VhhrnXIUDPdqn32', TRUE, TRUE)
ON CONFLICT DO NOTHING;

-- Insertar usuario normal
INSERT INTO users (username, email, hashed_password, is_admin, is_employee)
VALUES ('user1', 'user1@example.com', '$2b$12$XSI9yM9H7KTVU5j9AUKIqOBIRGc\r6NXrS5AEySHnx\XiWQ7HNONy', FALSE, TRUE)
ON CONFLICT DO NOTHING;

-- Insertar puertos de ejemplo
INSERT INTO ports (name, country, latitude, longitude) VALUES
('Puerto de Valencia', 'España', 39.4561, -0.3389),
('Puerto de Róterdam', 'Países Bajos', 51.9225, 4.4792),
('Puerto de Hamburgo', 'Alemania', 53.5511, 9.9937)
ON CONFLICT DO NOTHING;