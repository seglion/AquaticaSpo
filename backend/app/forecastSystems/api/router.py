# app/forecastSystems/api/routes.py

from app.forecastSystems.application.use_cases.ListForecastSystemsUseCase import ListForecastSystemsUseCase
from app.forecastSystems.application.use_cases.GetForecastSystemByIdUseCase import GetForecastSystemByIdUseCase
from app.forecastSystems.application.use_cases.DeleteForecastSystemUseCase import DeleteForecastSystemUseCase
from app.forecastSystems.application.use_cases.UpdateForecastSystemUseCase import UpdateForecastSystemUseCase
from app.contracts.infrastructure.infrastructure import ContractRepository
from app.forecastSystems.application.use_cases.GetForecastSystemByContractIdUseCase import GetForecastSystemByContractIdUseCase
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

# Importa los esquemas Pydantic que acabamos de definir
from app.forecastSystems.api.schemas import ForecastSystemCreate, ForecastSystemResponse, ForecastSystemUpdate

# Importa el modelo de dominio ForecastSystem (para la conversión a/desde Pydantic)
from app.forecastSystems.domain.models import ForecastSystem
from app.users.domain.models import User # Para el usuario autenticado

# Importa el repositorio concreto de la capa de infraestructura
from app.forecastSystems.infrastructure.infrastructure import SqlAlchemyForecastSystemRepository

# Importa los casos de uso específicos para ForecastSystem
from app.forecastSystems.application.use_cases.CreateForecastSystemUseCase import CreateForecastSystemUseCase




# Importa las dependencias compartidas para la sesión de DB y el usuario actual
from app.shared.dependencies import get_db_session
from app.shared.auth.dependencies import get_current_user

from sqlalchemy.ext.asyncio import AsyncSession

# Define el router de FastAPI para los sistemas de previsión
router = APIRouter(prefix="/forecast-systems", tags=["Forecast Systems"])

# --- Endpoints ---

@router.post("/", response_model=ForecastSystemResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast_system_api(
    system_create: ForecastSystemCreate,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Crea un nuevo sistema de previsión. Solo accesible para administradores.
    """
    # Control de permisos: solo administradores pueden crear
    if not requester.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear sistemas de previsión."
        )

    # Inicia el repositorio y el caso de uso
    repo = SqlAlchemyForecastSystemRepository(db)
    create_use_case = CreateForecastSystemUseCase(repo)

    # Convierte el DTO de Pydantic a tu modelo de dominio
    system_domain = ForecastSystem(
        id=None, # El ID será asignado por la base de datos
        name=system_create.name,

        contract_id=system_create.contract_id,
        port_id=system_create.port_id,
        hindcast_point_id=system_create.hindcast_point_id
    )
    
    try:
        # Ejecuta el caso de uso
        created_system = await create_use_case.execute(system_domain, requester) 
        # Convierte el modelo de dominio de vuelta a un DTO de Pydantic para la respuesta
        return ForecastSystemResponse.model_validate(created_system)
    except Exception as e:
        # Manejo general de errores. Excepciones específicas deben ser capturadas arriba.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el sistema de previsión: {e}"
        )

@router.get("/", response_model=List[ForecastSystemResponse])
async def list_forecast_system_api(
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
     Lista todos los sistemas de previsión disponibles.
    Solo accesible para empleados y administradores.
    """
    if not (requester.is_admin or requester.is_employee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para listar sistemas de previsión."
        )

    repo = SqlAlchemyForecastSystemRepository(db)
    list_use_case = ListForecastSystemsUseCase(repo)

    try:
        systems = await list_use_case.execute(requester)
        return [ForecastSystemResponse.model_validate(s) for s in systems]
    except PermissionError as e:  # Si el caso de uso tiene lógica de permisos más granular
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar sistemas de previsión: {e}"
        )
        
        
        
@router.get(
    "/{system_id}",
    response_model=ForecastSystemResponse
)
async def get_forecats_system_by_id_api(
    system_id: int,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Obtiene un sistema de previsión
    por su ID.
    """
    if not requester:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No tienes permiso "
                "para obtener sistemas "
                "de Prevision."
            )
        )

    repo = SqlAlchemyForecastSystemRepository(db)
    get_use_case = GetForecastSystemByIdUseCase(repo)

    try:
        system = await get_use_case.execute(
            system_id,
            requester
        )
        if not system:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Sistema  de "
                    "previsión no "
                    "encontrada."
                )
            )
        return ForecastSystemResponse.model_validate(system)
    except PermissionError as e:  # Captura si el caso de uso aún tiene lógica de permisos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Error al obtener el "
                f"sistema: {e}"
            )
        ) from e

        
        
@router.delete("/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_forecast_system_api(
    system_id: int,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Elimina una zona de previsión. Solo para administradores."""
    # Control de permisos directamente en el endpoint
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo los administradores pueden eliminar zsistemas de previsión.")

    repo = SqlAlchemyForecastSystemRepository(db)
    delete_use_case = DeleteForecastSystemUseCase(repo)

    try:
        await delete_use_case.execute(system_id,requester)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el sistema: {e}")

@router.put("/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
async def uodate_forecast_system_api(
    system_id: int,
    system_update: ForecastSystemUpdate,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Actualiza un sistema de previsión existente. Solo para administradores."""
    # Control de permisos directamente en el endpoint
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo los administradores pueden aactualizar sistemas de previsión.")

    repo = SqlAlchemyForecastSystemRepository(db)
    update_use_case = UpdateForecastSystemUseCase(repo)

    # Convertir Pydantic DTO a modelo de dominio, incluyendo el ID de la URL
    system_domain = ForecastSystem(
        id=system_id,
        name=system_update.name,
        port_id=system_update.port_id,
        forecast_system_id=system_update.forecast_system_id,
        hindcast_point_id=system_update.hindcast_point_id
    )


    try:
        await update_use_case.execute(system_domain,requester)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el sistema: {e}")



# --- Nuevo Endpoint: Obtener Sistema de Previsión por ID de Contrato ---
@router.get("/by-contract/{contract_id}", response_model=ForecastSystemResponse)
async def get_forecast_system_by_contract_id_api(
    contract_id: int,
    requester: User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db_session),
):
    """
    Obtiene un sistema de previsión asociado a un contrato específico.
    Los administradores pueden acceder a cualquiera. Los usuarios logueados solo a los
    asociados a sus contratos activos y vigentes.
    """
    if not requester:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Debe estar logueado para obtener esta información.")

    db_repo = SqlAlchemyForecastSystemRepository(db)
    contract_repo =  ContractRepository(db)  # Asegúrate de tener un repositorio de contratos para validar el contrato
    
    
    
    # La lógica de permisos y validación de contratos está en el caso de uso
    get_by_contract_use_case = GetForecastSystemByContractIdUseCase(db_repo, contract_repo)

    try:
        system = await get_by_contract_use_case.execute(contract_id, requester)
        if not system:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sistema de previsión asociado al contrato con ID {contract_id} no encontrado."
            )
        return ForecastSystemResponse.model_validate(system)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e: # Captura los errores de validación de contrato del caso de uso
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el sistema de previsión por ID de contrato: {e}"
        )
