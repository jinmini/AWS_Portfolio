from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from typing import List
from slugify import slugify
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.category import Category
from app.models.post import Post
from app.schemas.category import CategoryCreate, CategoryResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """카테고리 목록 조회"""
    try:
        query = select(Category).order_by(Category.name)
        result = await db.execute(query)
        categories = result.scalars().all()
        
        return [CategoryResponse.model_validate(category) for category in categories]
        
    except Exception as e:
        logger.error(f"카테고리 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카테고리 목록 조회에 실패했습니다"
        )

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """카테고리 상세 조회"""
    try:
        query = select(Category).where(Category.id == category_id)
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다"
            )
        
        return CategoryResponse.model_validate(category)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카테고리 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카테고리 조회에 실패했습니다"
        )

@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """슬러그로 카테고리 조회"""
    try:
        query = select(Category).where(Category.slug == slug)
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다"
            )
        
        return CategoryResponse.model_validate(category)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카테고리 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카테고리 조회에 실패했습니다"
        )

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """카테고리 생성 (로그인 필요)"""
    try:
        # 슬러그 검증 또는 자동 생성
        if not category_data.slug:
            slug = slugify(category_data.name)
        else:
            slug = category_data.slug
        
        # 슬러그 중복 체크
        existing = await db.execute(
            select(Category).where(Category.slug == slug)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 슬러그입니다"
            )
        
        # 카테고리 이름 중복 체크
        existing_name = await db.execute(
            select(Category).where(Category.name == category_data.name)
        )
        if existing_name.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 카테고리명입니다"
            )
        
        # 카테고리 생성
        category = Category(
            name=category_data.name,
            slug=slug,
            description=category_data.description
        )
        
        db.add(category)
        await db.commit()
        await db.refresh(category)
        
        logger.info(f"카테고리 생성됨: {category.id} - {category.name}")
        return CategoryResponse.model_validate(category)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"카테고리 생성 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카테고리 생성에 실패했습니다"
        )

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """카테고리 수정 (로그인 필요)"""
    try:
        # 카테고리 조회
        query = select(Category).where(Category.id == category_id)
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다"
            )
        
        # 슬러그 처리
        if not category_data.slug:
            slug = slugify(category_data.name)
        else:
            slug = category_data.slug
        
        # 슬러그 중복 체크 (자신 제외)
        existing = await db.execute(
            select(Category).where(
                Category.slug == slug,
                Category.id != category_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 슬러그입니다"
            )
        
        # 카테고리 이름 중복 체크 (자신 제외)
        existing_name = await db.execute(
            select(Category).where(
                Category.name == category_data.name,
                Category.id != category_id
            )
        )
        if existing_name.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 카테고리명입니다"
            )
        
        # 카테고리 업데이트
        category.name = category_data.name
        category.slug = slug
        category.description = category_data.description
        
        await db.commit()
        await db.refresh(category)
        
        logger.info(f"카테고리 수정됨: {category.id} - {category.name}")
        return CategoryResponse.model_validate(category)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"카테고리 수정 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카테고리 수정에 실패했습니다"
        )

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """카테고리 삭제 (로그인 필요)"""
    try:
        # 카테고리 조회
        query = select(Category).where(Category.id == category_id)
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다"
            )
        
        # 해당 카테고리를 사용하는 게시글이 있는지 확인
        posts_query = select(func.count(Post.id)).where(Post.category_id == category_id)
        posts_result = await db.execute(posts_query)
        posts_count = posts_result.scalar()
        
        if posts_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"해당 카테고리를 사용하는 게시글이 {posts_count}개 있습니다. 게시글을 먼저 삭제하거나 다른 카테고리로 이동해주세요."
            )
        
        await db.delete(category)
        await db.commit()
        
        logger.info(f"카테고리 삭제됨: {category_id} - {category.name}")
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"카테고리 삭제 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카테고리 삭제에 실패했습니다"
        )

@router.get("/{category_id}/posts")
async def get_category_posts(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """특정 카테고리의 게시글 수 조회"""
    try:
        # 카테고리 존재 확인
        category_query = select(Category).where(Category.id == category_id)
        category_result = await db.execute(category_query)
        category = category_result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다"
            )
        
        # 게시글 수 계산
        total_query = select(func.count(Post.id)).where(Post.category_id == category_id)
        published_query = select(func.count(Post.id)).where(
            Post.category_id == category_id,
            Post.is_published == True
        )
        
        total_result = await db.execute(total_query)
        published_result = await db.execute(published_query)
        
        total_posts = total_result.scalar()
        published_posts = published_result.scalar()
        
        return {
            "category": CategoryResponse.model_validate(category),
            "total_posts": total_posts,
            "published_posts": published_posts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카테고리 게시글 통계 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카테고리 게시글 통계 조회에 실패했습니다"
        ) 