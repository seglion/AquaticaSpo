# app/forecast_zones/presentation/api.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

# Importa los esquemas Pydantic para la entrada y salida de la API
from app.forecast_zones.api.schemas import ForecastZoneCreate, ForecastZoneResponse, ForecastZoneUpdate

# Importa los modelos de dominio (para la conversión)
from app.forecast_zones.domain.models import ForecastZone
from app.users.domain.models import User # Para el usuario autenticado

# Importa el repositorio concreto
from app.forecast_zones.infrastructure.infrastructure import ForecastZoneRepository

# Importa los casos de uso
from app.forecast_zones.application.use_cases.CreateForecastZoneUseCase import CreateForecastZoneUseCase
from app.forecast_zones.application.use_cases.GetForecastZoneUseCase import GetForecastZoneUseCase
from app.forecast_zones.application.use_cases.ListForecastZonesUseCase import ListForecastZonesUseCase
from app.forecast_zones.application.use_cases.UpdateForecastZoneUseCase import UpdateForecastZoneUseCase
from app.forecast_zones.application.use_cases.DeleteForecastZoneUseCase import DeleteForecastZoneUseCase
from app.forecast_zones.application.use_cases.ListForecastZonesForSystemUseCase import ListForecastZonesForSystemUseCase

# Importa las dependencias compartidas para la sesión de DB y el usuario actual
from app.shared.dependencies import get_db_session # Asumo que esta es la ruta correcta
from app.shared.auth.dependencies import get_current_user # Asumo que esta es la ruta correcta

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/forecast-zones", tags=["Forecast Zones"])

# --- Endpoints ---

@router.post("/", response_model=ForecastZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast_zone_api(
    zone_create: ForecastZoneCreate,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Crea una nueva zona de previsión. Solo para administradores."""
    # Control de permisos directamente en el endpoint
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo los administradores pueden crear zonas de previsión.")

    repo = ForecastZoneRepository(db)
    create_use_case = CreateForecastZoneUseCase(repo)

    # Convertir Pydantic DTO a modelo de dominio
    zone_domain = ForecastZone(
        id=None, # El ID será asignado por la BD
        name=zone_create.name,
        description=zone_create.description,
        forecast_system_id=zone_create.forecast_system_id,
        geom=zone_create.geom
    )
    
    try:
        # Pasa el requester al caso de uso, aunque la lógica de is_admin ya esté en el endpoint
        # El caso de uso puede tener sus propias validaciones o simplemente pasará el requester.
        created_zone = await create_use_case.execute(zone_domain, requester) 
        # Convertir modelo de dominio a Pydantic DTO para la respuesta
        return ForecastZoneResponse.model_validate(created_zone)
    except Exception as e:
        # Captura excepciones generales. Las excepciones específicas (PermissionError)
        # ya deberían haber sido manejadas por el if not requester.is_admin
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear la zona: {e}")

@router.get("/{zone_id}", response_model=ForecastZoneResponse)
async def get_forecast_zone_api(
    zone_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Obtiene una zona de previsión por su ID."""
    repo = ForecastZoneRepository(db)
    get_use_case = GetForecastZoneUseCase(repo)

    try:
        zone = await get_use_case.execute(zone_id)
        if not zone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona de previsión no encontrada.")
        return ForecastZoneResponse.model_validate(zone)
    except PermissionError as e: # Captura si el caso de uso aún tiene lógica de permisos
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener la zona: {e}")


@router.get("/", response_model=List[ForecastZoneResponse])
async def list_forecast_zones_api(
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Lista todas las zonas de previsión."""
    repo = ForecastZoneRepository(db)
    list_use_case = ListForecastZonesUseCase(repo)

    try:
        zones = await list_use_case.execute(requester)
        return [ForecastZoneResponse.model_validate(zone) for zone in zones]
    except PermissionError as e: # Captura si el caso de uso aún tiene lógica de permisos
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al listar zonas: {e}")
@router.put("/{zone_id}", response_model=ForecastZoneResponse)
async def update_forecast_zone_api(
    zone_id: int,
    zone_update: ForecastZoneUpdate,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Actualiza una zona de previsión existente. Solo para administradores."""
    # Control de permisos directamente en el endpoint
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo los administradores pueden actualizar zonas de previsión.")

    repo = ForecastZoneRepository(db)
    update_use_case = UpdateForecastZoneUseCase(repo)

    # Convertir Pydantic DTO a modelo de dominio, incluyendo el ID de la URL
    zone_domain = ForecastZone(
        id=zone_id,
        name=zone_update.name,
        description=zone_update.description,
        forecast_system_id=zone_update.forecast_system_id,
        geom=zone_update.geom
    )
    
    try:
        updated_zone = await update_use_case.execute(zone_domain, requester)
        return ForecastZoneResponse.model_validate(updated_zone)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar la zona: {e}")
    
    
@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_forecast_zone_api(
    zone_id: int,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Elimina una zona de previsión. Solo para administradores."""
    # Control de permisos directamente en el endpoint
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo los administradores pueden eliminar zonas de previsión.")

    repo = ForecastZoneRepository(db)
    delete_use_case = DeleteForecastZoneUseCase(repo)

    try:
        await delete_use_case.execute(zone_id, requester)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar la zona: {e}")

@router.get("/by-system/{system_id}", response_model=List[ForecastZoneResponse])
async def list_zones_by_system_api(
    system_id: int,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Lista las zonas de previsión asociadas a un sistema específico."""
    repo = ForecastZoneRepository(db)
    list_for_system_use_case = ListForecastZonesForSystemUseCase(repo)

    try:
        zones = await list_for_system_use_case.execute(system_id, requester)
        return [ForecastZoneResponse.model_validate(zone) for zone in zones]
    except PermissionError as e: # Captura si el caso de uso aún tiene lógica de permisos
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al listar zonas por sistema: {e}")
