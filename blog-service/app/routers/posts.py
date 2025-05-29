from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from slugify import slugify
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.post import Post, PostType
from app.models.category import Category
from app.models.tag import Tag
from app.schemas.post import (
    PostCreate, PostUpdate, PostResponse, 
    PostSummary, PostListResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=PostListResponse)
async def get_posts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=50, description="페이지 크기"),
    post_type: Optional[PostType] = Query(None, description="게시글 타입 (dev/esg)"),
    category_id: Optional[int] = Query(None, description="카테고리 ID"),
    published_only: bool = Query(True, description="발행된 게시글만"),
    sort_by: str = Query("created_at", description="정렬 기준"),
    sort_order: str = Query("desc", description="정렬 순서"),
    db: AsyncSession = Depends(get_db)
):
    """게시글 목록 조회 (페이지네이션)"""
    try:
        # 기본 쿼리
        query = select(Post).options(
            selectinload(Post.category),
            selectinload(Post.tags)
        )
        
        # 필터 조건
        filters = []
        if published_only:
            filters.append(Post.is_published == True)
        if post_type:
            filters.append(Post.post_type == post_type)
        if category_id:
            filters.append(Post.category_id == category_id)
            
        if filters:
            query = query.where(and_(*filters))
        
        # 정렬
        sort_column = getattr(Post, sort_by, Post.created_at)
        if sort_order == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # 전체 개수 계산
        count_query = select(func.count(Post.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 페이지네이션
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        
        result = await db.execute(query)
        posts = result.scalars().all()
        
        return PostListResponse(
            posts=[PostSummary.model_validate(post) for post in posts],
            total=total,
            page=page,
            size=size,
            total_pages=(total + size - 1) // size
        )
        
    except Exception as e:
        logger.error(f"게시글 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 목록 조회에 실패했습니다"
        )

@router.get("/search", response_model=PostListResponse)
async def search_posts(
    q: str = Query(..., description="검색어"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    post_type: Optional[PostType] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """게시글 검색"""
    try:
        # 검색 쿼리
        search_term = f"%{q}%"
        query = select(Post).options(
            selectinload(Post.category),
            selectinload(Post.tags)
        ).where(
            and_(
                Post.is_published == True,
                or_(
                    Post.title.ilike(search_term),
                    Post.content.ilike(search_term),
                    Post.summary.ilike(search_term)
                )
            )
        )
        
        if post_type:
            query = query.where(Post.post_type == post_type)
            
        # 관련도순 정렬 (제목 우선)
        query = query.order_by(desc(Post.created_at))
        
        # 전체 개수
        count_query = select(func.count(Post.id)).where(
            and_(
                Post.is_published == True,
                or_(
                    Post.title.ilike(search_term),
                    Post.content.ilike(search_term),
                    Post.summary.ilike(search_term)
                )
            )
        )
        if post_type:
            count_query = count_query.where(Post.post_type == post_type)
            
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 페이지네이션
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        
        result = await db.execute(query)
        posts = result.scalars().all()
        
        return PostListResponse(
            posts=[PostSummary.model_validate(post) for post in posts],
            total=total,
            page=page,
            size=size,
            total_pages=(total + size - 1) // size
        )
        
    except Exception as e:
        logger.error(f"게시글 검색 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 검색에 실패했습니다"
        )

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """게시글 상세 조회"""
    try:
        # 게시글 조회
        query = select(Post).options(
            selectinload(Post.category),
            selectinload(Post.tags),
            selectinload(Post.comments)
        ).where(Post.id == post_id)
        
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다"
            )
        
        # 조회수 증가
        post.view_count += 1
        await db.commit()
        
        return PostResponse.model_validate(post)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"게시글 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 조회에 실패했습니다"
        )

@router.get("/slug/{slug}")
async def get_post_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """슬러그로 게시글 조회 (MVP용 간소화 버전 - 읽기 전용)"""
    try:
        # 관계형 데이터 로딩 제거 - 기본 필드만 조회
        query = select(Post).where(Post.slug == slug)
        
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다"
            )
        
        # MVP용 간소화된 응답 데이터 구성 - 조회수 증가 제거
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "summary": post.summary,
            "slug": post.slug,
            "post_type": post.post_type.value,
            "is_published": post.is_published,
            "view_count": post.view_count,
            "created_at": post.created_at.isoformat(),
            "updated_at": post.updated_at.isoformat(),
            "author_id": post.author_id,
            "category": None,  # MVP용으로 null로 설정
            "tags": []  # MVP용으로 빈 배열로 설정
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"게시글 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 조회에 실패했습니다"
        )

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """게시글 생성 (로그인 필요)"""
    try:
        # 슬러그 생성
        base_slug = slugify(post_data.title)
        slug = base_slug
        counter = 1
        
        # 슬러그 중복 체크
        while True:
            existing = await db.execute(
                select(Post).where(Post.slug == slug)
            )
            if not existing.scalar_one_or_none():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # 게시글 생성
        post = Post(
            title=post_data.title,
            content=post_data.content,
            summary=post_data.summary,
            slug=slug,
            post_type=post_data.post_type,
            category_id=post_data.category_id,
            author_id=current_user_id,
            is_published=post_data.is_published
        )
        
        db.add(post)
        await db.flush()  # ID 생성을 위해
        
        # 태그 연결
        if post_data.tag_ids:
            tag_query = select(Tag).where(Tag.id.in_(post_data.tag_ids))
            tag_result = await db.execute(tag_query)
            tags = tag_result.scalars().all()
            post.tags.extend(tags)
        
        await db.commit()
        await db.refresh(post)
        
        # 관계 데이터 로드
        await db.refresh(post, ["category", "tags"])
        
        logger.info(f"게시글 생성됨: {post.id} - {post.title}")
        return PostResponse.model_validate(post)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"게시글 생성 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 생성에 실패했습니다"
        )

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """게시글 수정"""
    try:
        # 게시글 조회
        query = select(Post).options(
            selectinload(Post.category),
            selectinload(Post.tags)
        ).where(Post.id == post_id)
        
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다"
            )
        
        # 수정 권한 체크 (작성자만)
        if post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시글 수정 권한이 없습니다"
            )
        
        # 필드 업데이트
        update_data = post_data.model_dump(exclude_unset=True)
        
        if "tag_ids" in update_data:
            tag_ids = update_data.pop("tag_ids")
            # 기존 태그 제거
            post.tags.clear()
            # 새 태그 추가
            if tag_ids:
                tag_query = select(Tag).where(Tag.id.in_(tag_ids))
                tag_result = await db.execute(tag_query)
                tags = tag_result.scalars().all()
                post.tags.extend(tags)
        
        # 제목이 변경되면 슬러그도 업데이트
        if "title" in update_data:
            base_slug = slugify(update_data["title"])
            slug = base_slug
            counter = 1
            
            while True:
                existing = await db.execute(
                    select(Post).where(
                        and_(Post.slug == slug, Post.id != post_id)
                    )
                )
                if not existing.scalar_one_or_none():
                    break
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            post.slug = slug
        
        # 나머지 필드 업데이트
        for field, value in update_data.items():
            setattr(post, field, value)
        
        await db.commit()
        await db.refresh(post, ["category", "tags"])
        
        logger.info(f"게시글 수정됨: {post.id} - {post.title}")
        return PostResponse.model_validate(post)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"게시글 수정 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 수정에 실패했습니다"
        )

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """게시글 삭제"""
    try:
        # 게시글 조회
        query = select(Post).where(Post.id == post_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다"
            )
        
        # 삭제 권한 체크 (작성자만)
        if post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시글 삭제 권한이 없습니다"
            )
        
        await db.delete(post)
        await db.commit()
        
        logger.info(f"게시글 삭제됨: {post_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"게시글 삭제 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 삭제에 실패했습니다"
        )

@router.patch("/{post_id}/publish", response_model=PostResponse)
async def toggle_publish(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """게시글 발행/비발행 토글"""
    try:
        query = select(Post).where(Post.id == post_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다"
            )
        
        # 권한 체크
        if post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시글 발행 권한이 없습니다"
            )
        
        # 발행 상태 토글
        post.is_published = not post.is_published
        await db.commit()
        await db.refresh(post, ["category", "tags"])
        
        status_text = "발행" if post.is_published else "비발행"
        logger.info(f"게시글 {status_text}됨: {post.id}")
        
        return PostResponse.model_validate(post)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"게시글 발행 상태 변경 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 발행 상태 변경에 실패했습니다"
        ) 