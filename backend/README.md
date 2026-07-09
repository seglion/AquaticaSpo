# 🌊 AquaticaSpo Backend

> Servicio central para la gestión de datos oceanográficos y pronósticos de la plataforma AquaticaSpo.

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## 📖 Descripción

Este backend implementa la lógica de negocio core de **AquaticaSpo**, gestionando usuarios, contratos, sistemas de pronóstico y grandes volúmenes de datos oceanográficos. Está construido siguiendo los principios de **Clean Architecture** para asegurar escalabilidad y mantenibilidad.

## 🏗 Arquitectura

El proyecto sigue una estructura modular basada en **Clean Architecture**, separando responsabilidades en capas:

- **Domain**: Entidades y reglas de negocio puras.
- **Application**: Casos de uso y orquestación de la lógica.
- **Infrastructure**: Implementación de repositorios, bases de datos y adaptadores externos.
- **Ports**: Interfaces que definen los contratos entre capas.

### Módulos Principales

| Módulo | Descripción |
|--------|-------------|
| `users` | Gestión de usuarios, roles y autenticación (JWT). |
| `contracts` | Gestión de contratos comerciales asociados a usuarios. |
| `forecastSystems` | Configuración y gestión de sistemas de previsión. |
| `forecast_zones` | Definición de zonas geográficas de interés. |
| `hindcastPoint` | Puntos históricos de datos oceanográficos. |
| `downloadData` | Servicio de descarga y gestión de archivos de datos. |

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.12 o superior.
- PostgreSQL con extensión **PostGIS**.
- Docker (opcional, recomendado para desarrollo).

### Variables de Entorno
Crea un archivo `.env` en la raíz del backend basándote en el siguiente esquema:

```ini
# Base de Datos
POSTGRES_USER=usuario
POSTGRES_PASSWORD=password
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aquaticaspo

# Autenticación
JWT_SECRET_KEY=tu_clave_secreta_super_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# RabbitMQ (Opcional si se usa Worker)
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RABBITMQ_HOST=localhost
```

### Ejecutar Localmente

1.  **Crear entorno virtual**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

2.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Aplicar migraciones**:
    ```bash
    alembic upgrade head
    ```

4.  **Iniciar servidor**:
    ```bash
    uvicorn app.main:app --reload
    ```
    El servidor estará disponible en `http://localhost:8000`.

### Ejecutar con Docker

```bash
docker-compose up --build backend
```

## 🧪 Pruebas

El proyecto cuenta con una suite completa de tests unitarios y de integración usando `pytest`.

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=app tests/
```

## 📚 Documentación API

Una vez iniciado el servidor, puedes acceder a la documentación interactiva:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📂 Estructura de Directorios

```
backend/
├── alembic/              # Migraciones de base de datos
├── app/                  # Código fuente
│   ├── contracts/        # Módulo de Contratos
│   ├── forecastSystems/  # Módulo de Sistemas de Previsión
│   ├── users/            # Módulo de Usuarios
│   ├── shared/           # Utilidades compartidas (Config, Auth)
│   └── main.py           # Punto de entrada de la aplicación
├── tests/                # Tests automatizados
└── requirements.txt      # Dependencias del proyecto
```

---
Desarrollado para **Miguel Angel Vigo Baz**.
