from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer

from app.shared.dependencies import get_db_session
from app.shared.auth.jwt_service import JWTService
from app.shared.auth.password_hasher import verify_password,hash_password
from app.shared.config import settings

from app.users.infrastructure.infrastructure import UserRepository
from app.users.api.schemas import UserCreateSchema,UserResponseSchema,UserUpdateByAdminSchema,UserPasswordUpdateSchema
from app.users.domain.models import User

from app.users.application.use_cases.create_user import CreateUserUseCase
from app.users.application.use_cases.get_user import GetUserUseCase
from app.users.application.use_cases.update_user import UpdateUserUseCase
from app.users.application.use_cases.delete_user import DeleteUserUseCase
from app.users.application.use_cases.list_users import ListUsersUseCase
from app.shared.auth.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])
jwt_service = JWTService(secret_key=settings.JWT_SECRET_KEY)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def get_user_service(db: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)


# LOGIN
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
):
    repo = UserRepository(session)
    user = await repo.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    access_token = jwt_service.create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

# AUTH GUARD
async def is_admin_or_self(user: User, target_user_id: int):
    if not user.is_admin and user.id != target_user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso")




@router.post("/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateSchema,
    requester: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    if not requester.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para crear usuarios")
    repo = UserRepository(session)
    use_case = CreateUserUseCase(repo)
    
    user_to_create = User(
        id=None,
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_admin=payload.is_admin,
        is_employee=payload.is_employee,
    )
    
    created_user = await use_case.execute(user_to_create, requester)

    
    
    return created_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    requester: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = UserRepository(session)
    use_case = DeleteUserUseCase(repo)

    try:
        await use_case.execute(user_id, requester)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    return  # 204 No Content → no body

@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(
    user_id: int,
    requester: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = UserRepository(session)
    use_case = GetUserUseCase(repo)
    try:
        user = await use_case.execute(user_id, requester)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return user
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    
    
@router.get("/", response_model=List[UserResponseSchema])
async def list_users(
    requester: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = UserRepository(session)
    use_case = ListUsersUseCase(repo)
    try:
        return await use_case.execute(requester)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.put("/{user_id}", response_model=UserResponseSchema)

async def update_user(
    user_id: int,
    payload_admin: UserUpdateByAdminSchema = None,
    payload_user: UserPasswordUpdateSchema = None,
    requester: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = UserRepository(session)
    use_case = UpdateUserUseCase(repo)

    # Admin actualiza todo
    if requester.is_admin:
        if not payload_admin:
            raise HTTPException(status_code=400, detail="Faltan datos para actualización de administrador.")
        user_to_update = User(
            id=user_id,
            username=payload_admin.username,
            email=payload_admin.email,
            hashed_password=hash_password(payload_admin.password),
            is_admin=payload_admin.is_admin,
            is_employee=payload_admin.is_employee
        )
    else:
        if requester.id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para editar este usuario.")
        if not payload_user:
            raise HTTPException(status_code=400, detail="Faltan datos para cambiar la contraseña.")
        existing_user = await repo.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user_to_update = User(
            id=user_id,
            username=existing_user.username,
            email=existing_user.email,
            hashed_password=hash_password(payload_user.password),
            is_admin=existing_user.is_admin,
            is_employee=existing_user.is_employee
        )

    try:
        updated_user = await use_case.execute(user_to_update, requester)
        return updated_user
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))