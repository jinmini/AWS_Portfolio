from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    verify_token
)
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# 현재 사용자 가져오기 의존성
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """JWT 토큰에서 현재 사용자 정보 추출"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에서 사용자 ID를 찾을 수 없습니다"
        )
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다"
        )
    
    return user

# 관리자 권한 확인 의존성
async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """관리자 권한 확인"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user

@router.post("/register", response_model=UserResponse, summary="회원가입")
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    새 사용자 등록
    
    - **email**: 사용자 이메일 (고유값)
    - **password**: 비밀번호 (8자 이상 권장)
    - **full_name**: 사용자 이름 (선택사항)
    """
    # 이메일 중복 확인
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )
    
    # 비밀번호 해싱
    hashed_password = get_password_hash(user_data.password)
    
    # 새 사용자 생성
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        is_active=user_data.is_active
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"✅ 새 사용자 등록: {user_data.email}")
    return new_user

@router.post("/login", response_model=Token, summary="로그인")
async def login_user(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 로그인
    
    - **email**: 등록된 이메일
    - **password**: 비밀번호
    
    성공 시 JWT 액세스 토큰 반환
    """
    # 사용자 조회
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다"
        )
    
    # 비밀번호 확인
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다"
        )
    
    # 활성 사용자 확인
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비활성화된 계정입니다"
        )
    
    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": str(user.id)})
    
    logger.info(f"✅ 사용자 로그인: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse, summary="현재 사용자 정보")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    현재 로그인한 사용자의 정보 조회
    
    JWT 토큰이 필요합니다.
    """
    return current_user

@router.get("/users", response_model=list[UserResponse], summary="사용자 목록 조회 (관리자)")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    모든 사용자 목록 조회 (관리자만 가능)
    
    - **skip**: 건너뛸 레코드 수
    - **limit**: 가져올 최대 레코드 수
    """
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    
    logger.info(f"👥 사용자 목록 조회: {len(users)}명")
    return users

@router.put("/users/{user_id}/status", response_model=UserResponse, summary="사용자 상태 변경 (관리자)")
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 활성/비활성 상태 변경 (관리자만 가능)
    
    - **user_id**: 대상 사용자 ID
    - **is_active**: 활성화 여부 (true/false)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    
    status_text = "활성화" if is_active else "비활성화"
    logger.info(f"🔄 사용자 상태 변경: {user.email} -> {status_text}")
    
    return user 