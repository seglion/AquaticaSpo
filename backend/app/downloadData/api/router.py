from typing import List
from app.downloadData.domain.models import DownloadedData
from app.downloadData.application.use_cases.get_latest_downloaded_data_by_point import GetLatestDownloadedDataByPointUseCase
from app.downloadData.application.use_cases.list_all_downloadedData import ListAllDownloadedDataUseCase
from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from app.downloadData.api.schemas import DownloadedDataCreate, DownloadedDataRead
from app.downloadData.application.use_cases.add_downloaded_data import AddDownloadedDataUseCase
from app.downloadData.application.use_cases.get_downloaded_data_by_id import GetDownloadedDataByIdUseCase
from app.downloadData.infrastructure.infrastructure import DownloadedDataRepository
from app.users.domain.models import User
from app.shared.dependencies import get_db_session
from app.shared.auth.dependencies import get_current_user

from sqlalchemy.ext.asyncio import AsyncSession # type: ignore

router = APIRouter(prefix="/downloaded-data", tags=["Downloaded Data"])

@router.post("/", response_model=DownloadedDataRead, status_code=status.HTTP_201_CREATED)
async def add_downloaded_data(
    payload: DownloadedDataCreate,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para añadir datos descargados")

    repo = DownloadedDataRepository(db)
    use_case = AddDownloadedDataUseCase(repo)

    downloaded_data = DownloadedData(
        id=None,
        point_id=payload.point_id,
        downloaded_at=payload.downloaded_at,
        data=payload.data
    )

    created_data = await use_case.execute(downloaded_data,requester)
    return created_data





@router.get("/{downloaded_data_id}", response_model=DownloadedDataRead)
async def get_downloaded_data_by_id(
    downloaded_data_id: int,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    repo = DownloadedDataRepository(db)
    use_case = GetDownloadedDataByIdUseCase(repo)

    try:
        data = await use_case.execute(downloaded_data_id, requester)
        return data
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
    
@router.get("/latest/by-point/{point_id}", response_model=DownloadedDataRead)
async def get_latest_downloaded_data_by_point(
    point_id: int,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    repo = DownloadedDataRepository(db)
    use_case = GetLatestDownloadedDataByPointUseCase(repo)

    try:
        data = await use_case.execute(point_id, requester)
        return data
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
    
@router.get("/", response_model=List[DownloadedDataRead])
async def list_all_downloaded_data(
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    repo = DownloadedDataRepository(db)
    use_case = ListAllDownloadedDataUseCase(repo)

    try:
        data = await use_case.execute(requester)
        return data
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))