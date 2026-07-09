from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict

class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_admin: bool = False
    is_employee: bool = False

class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool
    is_employee: bool
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdateByAdminSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_admin: bool
    is_employee: bool

class UserPasswordUpdateSchema(BaseModel):
    password: str