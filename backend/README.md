# Backend AquaticaSpo

Este backend implementa la lógica de negocio y la API para la plataforma AquaticaSpo, gestionando usuarios, contratos, sistemas de previsión, zonas, resultados y datos oceanográficos.

## Tecnologías principales
- Python 3.12+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL + PostGIS
- Alembic (migraciones)
- Pydantic
- Docker (opcional)

## Estructura de carpetas
- `app/` Código fuente principal
  - `shared/` Configuración, base, dependencias comunes
  - `users/` Gestión de usuarios
  - `contracts/` Contratos y relación con usuarios
  - `ports/` Puertos
  - `hindcastPoint/` Puntos de hindcast
  - `downloadData/` Descarga de datos oceanográficos
  - `forecastSystems/` Sistemas de previsión
  - `forecast_zones/` Zonas de previsión
  - `forecast_system_results/` Resultados de sistemas de previsión
  - `tests/` Pruebas unitarias y de integración
- `alembic/` Migraciones de base de datos
- `initdb/` Scripts SQL de inicialización

## Configuración y ejecución

### 1. Variables de entorno
Configura las variables necesarias (puedes usar `.env`):
- `DATABASE_URL` (ejemplo: `postgresql+asyncpg://usuario:password@localhost:5432/aquaticaspo`)
- Otros según necesidades de autenticación, etc.

### 2. Instalación de dependencias
```bash
pip install -r requirements.txt
```

### 3. Migraciones de base de datos
```bash
alembic upgrade head
```

### 4. Inicialización de la base de datos (opcional)
Puedes cargar datos de ejemplo con:
```bash
psql -U usuario -d aquaticaspo -f initdb/init.sql
```

### 5. Ejecución del servidor
```bash
uvicorn app.main:app --reload
```

## Endpoints principales
- `/users` Gestión de usuarios
- `/contracts` Contratos y asignación a usuarios
- `/ports` Puertos
- `/hindcast-points` Puntos de hindcast
- `/download-data` Descarga de datos
- `/forecast-systems` Sistemas de previsión
- `/forecast-zones` Zonas de previsión
- `/forecast-results` Resultados de previsión

## Pruebas
```bash
pytest
```

## Notas
- El backend requiere una base de datos PostgreSQL con la extensión PostGIS habilitada.
- Para desarrollo local puedes usar Docker y docker-compose.
- Consulta la documentación interna de cada módulo para detalles de uso y modelos.
