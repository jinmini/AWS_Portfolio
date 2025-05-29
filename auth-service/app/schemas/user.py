from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 사용자 기본 스키마
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

# 사용자 생성 스키마
class UserCreate(UserBase):
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "full_name": "홍길동"
            }
        }

# 사용자 응답 스키마
class UserResponse(UserBase):
    id: int
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 로그인 스키마
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@jinmini.com",
                "password": "admin123"
            }
        }

# 토큰 스키마
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# 토큰 데이터 스키마
class TokenData(BaseModel):
    user_id: Optional[int] = None 