# app/ports/api/router.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import get_db_session

from app.ports.infrastructure.infrastructure import PortRepository
from app.ports.api.schemas import PortCreate, PortRead, PortUpdate
from app.ports.domain.models import Port

router = APIRouter(prefix="/ports", tags=["ports"])


def get_port_service(
    db: AsyncSession = Depends(get_db_session),
) -> PortRepository:
    return PortRepository(db)

@router.post("/", response_model=PortRead, status_code=status.HTTP_201_CREATED)
async def create_port(
    payload: PortCreate,
    service: PortRepository = Depends(get_port_service),
):
    try:
        return await service.create_port(
            payload.name, payload.country, payload.latitude, payload.longitude
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{port_id}", response_model=PortRead)
async def read_port(
    port_id: int,
    service: PortRepository = Depends(get_port_service),
):
    port = await service.get_port_by_id(port_id)
    if not port:
        raise HTTPException(status_code=404, detail="Port not found")
    return port

@router.get("/", response_model=List[PortRead])
async def list_ports(
    service: PortRepository = Depends(get_port_service),
):
    return await service.list_ports()

@router.put("/{port_id}", response_model=PortRead)
async def update_port(
    port_id: int,
    payload: PortUpdate,
    service: PortRepository = Depends(get_port_service),
):
    port = await service.update_port(
        port_id,
        name=payload.name,
        country=payload.country,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    if not port:
        raise HTTPException(status_code=404, detail="Port not found")
    return port

@router.delete("/{port_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_port(
    port_id: int,
    service: PortRepository = Depends(get_port_service),
):
    success = await service.delete_port(port_id)
    if not success:
        raise HTTPException(status_code=404, detail="Port not found")
    return