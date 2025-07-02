from app.users.infrastructure.infrastructure import UserRepository
from fastapi import APIRouter, Depends, HTTPException, status# type: ignore
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession # type: ignore

from app.shared.dependencies import get_db_session
from app.shared.auth.dependencies import get_current_user
from app.contracts.api.schemas import (
    ContractCreate,
    ContractUpdate,
    ContractOut,
    ContractToUserBase,
    RemoveContractFromUserBase,
)
from app.contracts.infrastructure.infrastructure import ContractRepository
from app.contracts.application.use_cases.CreateContractUseCase import CreateContractUseCase
from app.contracts.application.use_cases.GetContractUseCase import GetContractUseCase
from app.contracts.application.use_cases.UpdateContractUseCase import UpdateContractUseCase
from app.contracts.application.use_cases.DeleteContractUseCase import DeleteContractUseCase

from app.contracts.application.use_cases.ListContractsForUserUseCase import ListContractsForUserUseCase
from app.contracts.application.use_cases.AddContractToUserUseCase import AddContractToUserUseCase
from app.contracts.application.use_cases.RemoveContractFromUserUseCase import RemoveContractToUserUseCase
from app.users.domain.models import User

router = APIRouter(prefix="/contracts", tags=["contracts"])


def get_contract_repo(db: AsyncSession = Depends(get_db_session)) -> ContractRepository:
    return ContractRepository(db)

@router.get("/my", response_model=List[ContractOut])
async def list_contracts_for_user(
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    repo = ContractRepository(db)
    use_case = ListContractsForUserUseCase(repo)

    try:
        contracts = await use_case.execute(requester)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return contracts

@router.delete("/remove-from-user", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contract_from_user(
    payload: RemoveContractFromUserBase,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para esta acción")

    contract_repo = ContractRepository(db)
    user_repo = UserRepository(db)
    use_case = RemoveContractToUserUseCase(contract_repo, user_repo)

    try:
        await use_case.execute(payload.contract_id, payload.user_id, requester)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return





@router.get("/{contract_id}", response_model=ContractOut)
async def get_contract(
    contract_id: int,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ContractRepository(db)
    use_case = GetContractUseCase(repo)
    
    try:
        contract = await use_case.execute(contract_id, requester)
        if contract is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato no encontrado")
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return contract


@router.post("/", response_model=ContractOut, status_code=status.HTTP_201_CREATED)
async def create_contract(
    payload: ContractCreate,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para crear contratos")

    repo = ContractRepository(db)
    use_case = CreateContractUseCase(repo)

    contract_to_create = payload  # payload ya es ContractCreate

    created_contract = await use_case.execute(contract_to_create, requester)
    return created_contract



@router.post("/assign", status_code=status.HTTP_204_NO_CONTENT)
async def assign_contract_to_user(
    payload: ContractToUserBase,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    if not requester.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para asignar contratos"
        )

    contract_repo = ContractRepository(db)
    from app.users.infrastructure.infrastructure import UserRepository  # importa tu repo real de users
    user_repo = UserRepository(db)

    use_case = AddContractToUserUseCase(contract_repo, user_repo)

    try:
        await use_case.execute(payload.contract_id, payload.user_id, requester)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return  # 204 No Content




@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: int,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ContractRepository(db)
    use_case = DeleteContractUseCase(repo)
    
    try:
        await use_case.execute(contract_id, requester)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    return None  # 204 No Content no devuelve body

@router.put("/{contract_id}", response_model=ContractOut)
async def update_contract(
    contract_id: int,
    payload: ContractUpdate,
    requester: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ContractRepository(db)
    use_case = UpdateContractUseCase(repo)

    existing_contract = await repo.get_contract_by_id(contract_id)
    if not existing_contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    if not requester.is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar contratos")

    # Actualiza manualmente los campos que estén en payload
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_contract, key, value)

    updated_contract = await use_case.execute(existing_contract, requester)
    return updated_contract