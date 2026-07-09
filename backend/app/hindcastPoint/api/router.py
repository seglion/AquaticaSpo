from app.hindcastPoint.domain.models import HindcastPoint
from app.hindcastPoint.application.use_cases.GetHindcastPointUseCase import GetContractUseCase
from app.hindcastPoint.application.use_cases.ListHindcastPointUseCase import ListHindCastPointUseCase
from app.hindcastPoint.application.use_cases.UpdateHindcastPointUseCase import UpdateHindCastPointUseCase
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.hindcastPoint.infrastructure.infrastructure import HindcastPointRepository

from app.hindcastPoint.api.schemas import (
    HindcastPointCreate,
    HindcastPointUpdate,
    HindcastPointRead
)
from app.users.domain.models import User
from app.shared.dependencies import get_db_session
from app.shared.auth.dependencies import get_current_user
from app.hindcastPoint.application.use_cases.CreateHindcastPointUseCase import CreateHindcasPointtUseCase
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/hindcast-points", tags=["Hindcast Points"])


@router.post("/", response_model=HindcastPointRead, status_code=status.HTTP_201_CREATED)
async def create_hindcast_point(
    payload: HindcastPointCreate,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para crear puntos hindcast")

    repo = HindcastPointRepository(db)
    use_case = CreateHindcasPointtUseCase(repo)

    hindcast_point = HindcastPoint(
        id=None,
        latitude=payload.latitude,
        longitude=payload.longitude,
        url=payload.url,
        models=payload.models
    )

    created_point = await use_case.execute(hindcast_point, requester)
    return created_point

@router.get("/{hindcast_point_id}", response_model=HindcastPointRead)
async def get_hindcast_point(
    hindcast_point_id: int,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para obtener puntos hindcast")

    repo = HindcastPointRepository(db)
    use_case = GetContractUseCase(repo)

    point = await use_case.execute(hindcast_point_id, requester)
    if point is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto hindcast no encontrado")
    return point

@router.get("/", response_model=List[HindcastPointRead])
async def list_hindcast_points(
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para obtener puntos hindcast")

    repo = HindcastPointRepository(db)
    use_case = ListHindCastPointUseCase(repo)

    points = await use_case.execute(requester)
    return points


@router.put("/{hindcast_point_id}", response_model=HindcastPointRead)
async def update_hindcastPoint(
    hindcast_point_id: int,
    payload: HindcastPointUpdate,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    if not requester.is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso")

    repo = HindcastPointRepository(db)
    use_case = UpdateHindCastPointUseCase(repo)

    updated_data = payload.dict(exclude_unset=True)  # Solo campos actualizados
    updated_point = await use_case.execute(hindcast_point_id, updated_data, requester)
    return updated_point