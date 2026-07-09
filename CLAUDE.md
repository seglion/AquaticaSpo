# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AquaticaSpo is a platform for managing oceanographic forecast systems. It is a monorepo with four services that work together:

- **`backend/`** — FastAPI REST API (Python 3.12, async SQLAlchemy, PostgreSQL+PostGIS)
- **`cron/`** — Scheduled Python service that triggers data downloads every 30 minutes via RabbitMQ
- **`forecastWorker/`** — Python worker that consumes RabbitMQ messages, runs SWAN wave propagation, and saves forecast results
- **`frontend/`** — Vue 3 + TypeScript SPA (Vite, Pinia, TailwindCSS v4, Vue Router)

The full stack is orchestrated via `docker-compose.yml` at the root.

## Commands

### Backend

```bash
cd backend
python -m venv venv && venv\Scripts\activate  # Windows
pip install -r requirements.txt
alembic upgrade head                          # Apply DB migrations
uvicorn app.main:app --reload                 # Dev server at http://localhost:8000
```

Run tests (from `backend/`):
```bash
pytest                                        # All tests
pytest tests/contracts/                       # Single module
pytest tests/contracts/application/use_cases/test_create_contract_use_case.py  # Single file
pytest --cov=app tests/                       # With coverage
```

Tests run in `asyncio_mode = auto` — no `@pytest.mark.asyncio` needed per test. Tests hit a **real database** (configured via `.env`), not mocks.

### Frontend

```bash
cd frontend
npm install
npm run dev          # Dev server at http://localhost:5173
npm run build        # Production build (runs vue-tsc then vite build)
```

### Docker (full stack)

```bash
docker-compose up --build           # Build and start all services
docker-compose up -d cron worker    # Start background services
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"   # Generate migration
alembic upgrade head                                # Apply migrations
alembic downgrade -1                               # Rollback one step
```

## Architecture

### Backend — Clean Architecture

Every domain module (`contracts`, `users`, `forecastSystems`, `hindcastPoint`, `downloadData`, `forecast_zones`, `forecast_system_results`, `ports`) follows the same four-layer structure:

```
app/<module>/
├── domain/models.py          # Plain Python dataclasses (business entities)
├── application/
│   ├── repositories.py       # Abstract base classes (interfaces)
│   └── use_cases/            # One class per use case; receives repo + requester: User
├── infrastructure/
│   ├── models.py             # SQLAlchemy ORM + orm_to_domain / domain_to_orm helpers
│   └── repositories.py       # Concrete async SQLAlchemy implementation of the ABC
└── api/
    ├── router.py             # FastAPI router; injects DB session + current_user
    └── schemas.py            # Pydantic request/response schemas
```

**Key conventions:**
- Domain models are plain `@dataclass`; they never import SQLAlchemy.
- Each infrastructure `models.py` contains `orm_to_domain()` and `domain_to_orm()` conversion functions — no ORM objects cross layer boundaries.
- Use cases receive a `requester: User` parameter for authorization. Permission checks are `if not requester.is_admin: raise PermissionError(...)`.
- `User` has `is_admin: bool`, `is_employee: bool`, `contracts: List[Contract]` (eager-loaded), and `session_USER` (JWT token, set by infrastructure layer after login).
- Database URL uses `asyncpg` driver: `postgresql+asyncpg://...`

### ForecastWorker

The worker connects to RabbitMQ exchange `forecast_tasks_exchange`, receives JSON messages with `forecast_system_id` and `downloaded_data_id`, then:
1. Authenticates against the backend API (via `API_USER`/`API_PASSWORD` env vars)
2. Fetches forecast system config, forecast zones, and hindcast data from the backend REST API
3. Applies direction-based calibration using `.mat` files in `forecastWorker/app/assets/calibration_params/<model>/`
4. Runs SWAN wave propagation using pre-computed lookup tables (`.npz` files) in `forecastWorker/app/assets/swan/`
5. Posts results back to the backend via `POST /forecast-results/`

Propagation output format: `{ "<model>": { "timestamps": [...], "zones": { "<zone_name>": { "Hs": [...], "Tp": [...], "PeakDirection": [...] } } } }`

### Frontend

Vue 3 Composition API with `<script setup>`. State managed by Pinia stores (`access.store.ts`, `forecast.store.ts`). Atomic design for components: `atoms/` → `molecules/` → `organisms/` → `templates/`. Routes are lazy-loaded; navigation guard checks `accessStore.isAuthenticated` before entering any route with `meta: { requiresAuth: true }`. Vite proxies `/api/meteogalicia` to avoid CORS with the MeteoGalicia external API.

## Environment Variables

Create a `.env` file at the repository root (used by Docker) and another inside `backend/` (used for local runs):

```ini
# Database (PostGIS required)
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_SERVER=localhost    # 'db' inside Docker
POSTGRES_PORT=5432
POSTGRES_DB=aquaticaspo

# Auth
JWT_SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RABBITMQ_HOST=localhost      # 'rabbitmq' inside Docker

# Cron & Worker identity
API_USER=
API_PASSWORD=

# Worker → Backend communication
BACKEND_API_URL=http://localhost:8000   # 'http://api:8000' inside Docker
```

## API Documentation

When the backend is running: Swagger UI at `http://localhost:8000/docs`, ReDoc at `http://localhost:8000/redoc`.
