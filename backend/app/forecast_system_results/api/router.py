# app/forecast_system_results/api/routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# Importa los esquemas Pydantic
from app.forecast_system_results.api.schemas import ForecastSystemResultCreate, ForecastSystemResultResponse, PaginatedForecastSystemResults

# Importa el modelo de dominio ForecastSystemResult (para la conversión a/desde Pydantic)
from app.forecast_system_results.domain.models import ForecastSystemResult # Asume que tienes este modelo
from app.users.domain.models import User # Para el usuario autenticado

# Importa los repositorios concretos de la capa de infraestructura
from app.forecast_system_results.infrastructure.infrastucture import SQLAlchemyForecastSystemResultRepository # Asume esta ruta y clase
from app.forecast_zones.infrastructure.infrastructure import ForecastZoneRepository as SQLAlchemyForecastZoneRepository # Necesario para validar zonas

# Importa los casos de uso específicos para ForecastSystemResult
from app.forecast_system_results.application.use_cases.CreateForecastSystemResultUseCase import CreateForecastSystemResultUseCase
from app.forecast_system_results.application.use_cases.GetForecastSystemResultByIdUseCase import GetForecastSystemResultByIdUseCase
from app.forecast_system_results.application.use_cases.ListForecastSystemResultsByZoneUseCase import ListForecastSystemResultsByZoneUseCase
from app.forecast_system_results.application.use_cases.GetLatestForecastSystemResultByZoneUseCase import GetLatestForecastSystemResultByZoneUseCase
from app.forecast_system_results.application.use_cases.DeleteForecastSystemResultUseCase import DeleteForecastSystemResultUseCase

# Importa las dependencias compartidas para la sesión de DB y el usuario actual
from app.shared.dependencies import get_db_session
from app.shared.auth.dependencies import get_current_user # Asume esta ruta

from sqlalchemy.ext.asyncio import AsyncSession

# Define el router de FastAPI para los resultados de sistemas de previsión
router = APIRouter(prefix="/forecast-results", tags=["Forecast System Results"])

# --- Endpoints ---

@router.get("/{result_id}", response_model=ForecastSystemResultResponse)
async def get_forecast_system_result_by_id_api(
    result_id: int = Path(..., description="ID del resultado de previsión a obtener."),
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Obtiene un resultado de previsión por su ID. Solo accesible para administradores y empleados.
    """
    if not (requester.is_admin or requester.is_employee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para obtener resultados de previsión."
        )

    result_repo = SQLAlchemyForecastSystemResultRepository(db)
    zone_repo = SQLAlchemyForecastZoneRepository(db) # Podría ser necesario para el caso de uso
    get_use_case = GetForecastSystemResultByIdUseCase(result_repo, zone_repo) # Si tu caso de uso lo requiere

    try:
        result = await get_use_case.execute(result_id, requester)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resultado de previsión con ID {result_id} no encontrado."
            )
        return ForecastSystemResultResponse.model_validate(result)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el resultado de previsión: {e}"
        )


@router.post("/", response_model=ForecastSystemResultResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast_system_result_api(
    result_create: ForecastSystemResultCreate,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Crea un nuevo resultado de previsión. Solo accesible para administradores y empleados.
    """
    # Control de permisos: solo administradores o empleados pueden crear
    if not (requester.is_admin or requester.is_employee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores y empleados pueden crear resultados de previsión."
        )

    # Inicia los repositorios y el caso de uso
    result_repo = SQLAlchemyForecastSystemResultRepository(db)
    zone_repo = SQLAlchemyForecastZoneRepository(db) # Necesario para validar la zona de previsión
    create_use_case = CreateForecastSystemResultUseCase(result_repo, zone_repo)

    # No es necesario convertir a modelo de dominio aquí si el caso de uso acepta DTOs o datos crudos.
    # Si tu caso de uso espera un modelo de dominio, harías la conversión aquí:
    # result_domain = ForecastSystemResult(
    #     id=None,
    #     forecast_zone_id=result_create.forecast_zone_id,
    #     execution_date=datetime.now(), # O se recibe en el DTO
    #     result_data=result_create.result_data
    # )
    
    try:
        # Ejecuta el caso de uso, pasando los datos necesarios.
        # Asumo que el caso de uso es inteligente para manejar los campos.
        created_result = await create_use_case.execute(
            forecast_zone_id=result_create.forecast_zone_id,
            result_data=result_create.result_data,
            requester=requester
        )
        # Convierte el modelo de dominio de vuelta a un DTO de Pydantic para la respuesta
        return ForecastSystemResultResponse.model_validate(created_result)
    except ValueError as e: # Por ejemplo, si la forecast_zone_id no existe o es inválida
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el resultado de previsión: {e}"
        )

@router.get("/", response_model=PaginatedForecastSystemResults)
async def list_forecast_system_results_api(
    zone_id: int = Query(..., description="ID de la zona de previsión a listar."), # Hacemos zone_id obligatorio aquí
  
    page: int = Query(1, ge=1, description="Número de página para la paginación."),
    page_size: int = Query(10, ge=1, le=100, description="Cantidad de resultados por página."),
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Lista los resultados de previsión con opciones de filtrado y paginación para una zona específica.
    Accesible para administradores, empleados y usuarios con contrato para las zonas relevantes.
    """
    result_repo = SQLAlchemyForecastSystemResultRepository(db)
    zone_repo = SQLAlchemyForecastZoneRepository(db)
    list_use_case = ListForecastSystemResultsByZoneUseCase(result_repo, zone_repo)

    try:
        # El caso de uso ListForecastSystemResultsByZoneUseCase espera limit y offset
        offset = (page - 1) * page_size
        results_list_uc = await list_use_case.execute(
            zone_id=zone_id,
            requester=requester,
            limit=page_size,
            offset=offset,
            # Aquí podríamos pasar start_date y end_date si el caso de uso los soporta
            # De lo contrario, la lógica de filtrado por fechas debería estar en el repo o UCs más específicos
        )
        # Adaptar la respuesta del caso de uso a PaginatedForecastSystemResults
        return PaginatedForecastSystemResults(
            items=[ForecastSystemResultResponse.model_validate(r) for r in results_list_uc],
 # Necesitas que el caso de uso devuelva el total_count
            page=page,
            page_size=page_size,
                limit=page_size,
    offset=offset
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar resultados de previsión: {e}"
        )
@router.get("/latest-by-zone/{zone_id}", response_model=ForecastSystemResultResponse)
async def get_latest_forecast_system_result_by_zone_api(
    zone_id: int = Path(..., description="ID de la zona de previsión para obtener el último resultado."),
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Obtiene el resultado de previsión más reciente para una zona específica.
    Accesible para administradores, empleados y usuarios con contrato para la zona.
    """
    # Inicializa los repositorios
    result_repo = SQLAlchemyForecastSystemResultRepository(db)
    zone_repo = SQLAlchemyForecastZoneRepository(db)

    # Inicializa el caso de uso con los repositorios
    get_latest_use_case = GetLatestForecastSystemResultByZoneUseCase(result_repo, zone_repo)

    try:
        # Ejecuta el caso de uso, pasando el ID de la zona y el usuario que lo solicita
        latest_result = await get_latest_use_case.execute(zone_id, requester)
        
        # Si el caso de uso no devuelve ningún resultado, lanza un 404
        if not latest_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron resultados para la zona con ID {zone_id}."
            )
        
        # Convierte el modelo de dominio a un esquema de respuesta Pydantic
        return ForecastSystemResultResponse.model_validate(latest_result)
    
    except PermissionError as e:
        # Captura errores de permiso lanzados por el caso de uso y los mapea a un 403
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    
    except ValueError as e:
        # Captura errores de valor (ej. zona no existe) lanzados por el caso de uso y los mapea a un 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception as e:
        # Captura cualquier otra excepción inesperada y la mapea a un 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el último resultado de previsión: {e}"
        )
# --- Endpoint para eliminar un resultado de previsión ---

@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_forecast_system_result_api(
    result_id: int = Path(..., description="ID del resultado de previsión a eliminar."),
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Elimina un resultado de previsión por su ID. Solo accesible para administradores.
    """
    # Inicializa el repositorio
    result_repo = SQLAlchemyForecastSystemResultRepository(db)
    
    # Inicializa el caso de uso
    delete_use_case = DeleteForecastSystemResultUseCase(result_repo)

    try:
        # Ejecuta el caso de uso, pasando el ID del resultado a eliminar y el usuario que lo solicita
        deleted = await delete_use_case.execute(result_id, requester)
        
        # Aunque el caso de uso ya lanza un ValueError si no se encuentra el ID,
        # es una buena práctica asegurar la respuesta 404 en el API si `deleted` es False.
        # Sin embargo, dado que el caso de uso lanza un ValueError en ese escenario,
        # la excepción se capturará abajo.
        if not deleted:
            # Esta línea solo se alcanzaría si el caso de uso cambiara su comportamiento
            # y no lanzara una excepción para "no encontrado". Con tu UC actual,
            # la excepción se maneja en el bloque `except ValueError`.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resultado de previsión con ID {result_id} no encontrado."
            )
        
        # FastAPI devuelve automáticamente 204 No Content para endpoints sin response_model
        # y que no devuelven nada explícitamente.
        return # No se devuelve contenido para una respuesta 204 No Content

    except PermissionError as e:
        # Captura errores de permiso lanzados por el caso de uso y los mapea a un 403
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    
    except ValueError as e:
        # Captura errores de valor (ej. resultado no existe) lanzados por el caso de uso
        # y los mapea a un 404 Not Found.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except Exception as e:
        # Captura cualquier otra excepción inesperada y la mapea a un 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el resultado de previsión: {e}"
        )
