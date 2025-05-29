from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from typing import List
from slugify import slugify
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.tag import Tag
from app.models.post import Post, post_tags
from app.schemas.tag import TagCreate, TagResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[TagResponse])
async def get_tags(
    db: AsyncSession = Depends(get_db)
):
    """태그 목록 조회"""
    try:
        query = select(Tag).order_by(Tag.name)
        result = await db.execute(query)
        tags = result.scalars().all()
        
        return [TagResponse.model_validate(tag) for tag in tags]
        
    except Exception as e:
        logger.error(f"태그 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="태그 목록 조회에 실패했습니다"
        )

@router.get("/popular", response_model=List[dict])
async def get_popular_tags(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """인기 태그 목록 (게시글 수 기준)"""
    try:
        # 태그별 게시글 수 계산
        query = select(
            Tag,
            func.count(post_tags.c.post_id).label('post_count')
        ).outerjoin(
            post_tags
        ).group_by(
            Tag.id
        ).order_by(
            desc('post_count')
        ).limit(limit)
        
        result = await db.execute(query)
        tag_stats = result.all()
        
        return [
            {
                "tag": TagResponse.model_validate(tag),
                "post_count": count
            }
            for tag, count in tag_stats
        ]
        
    except Exception as e:
        logger.error(f"인기 태그 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="인기 태그 조회에 실패했습니다"
        )

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    """태그 상세 조회"""
    try:
        query = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="태그를 찾을 수 없습니다"
            )
        
        return TagResponse.model_validate(tag)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"태그 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="태그 조회에 실패했습니다"
        )

@router.get("/slug/{slug}", response_model=TagResponse)
async def get_tag_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """슬러그로 태그 조회"""
    try:
        query = select(Tag).where(Tag.slug == slug)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="태그를 찾을 수 없습니다"
            )
        
        return TagResponse.model_validate(tag)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"태그 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="태그 조회에 실패했습니다"
        )

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """태그 생성 (로그인 필요)"""
    try:
        # 슬러그 검증 또는 자동 생성
        if not tag_data.slug:
            slug = slugify(tag_data.name)
        else:
            slug = tag_data.slug
        
        # 슬러그 중복 체크
        existing = await db.execute(
            select(Tag).where(Tag.slug == slug)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 슬러그입니다"
            )
        
        # 태그 이름 중복 체크
        existing_name = await db.execute(
            select(Tag).where(Tag.name == tag_data.name)
        )
        if existing_name.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 태그명입니다"
            )
        
        # 태그 생성
        tag = Tag(
            name=tag_data.name,
            slug=slug
        )
        
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        
        logger.info(f"태그 생성됨: {tag.id} - {tag.name}")
        return TagResponse.model_validate(tag)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"태그 생성 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="태그 생성에 실패했습니다"
        )

@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """태그 수정 (로그인 필요)"""
    try:
        # 태그 조회
        query = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="태그를 찾을 수 없습니다"
            )
        
        # 슬러그 처리
        if not tag_data.slug:
            slug = slugify(tag_data.name)
        else:
            slug = tag_data.slug
        
        # 슬러그 중복 체크 (자신 제외)
        existing = await db.execute(
            select(Tag).where(
                Tag.slug == slug,
                Tag.id != tag_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 슬러그입니다"
            )
        
        # 태그 이름 중복 체크 (자신 제외)
        existing_name = await db.execute(
            select(Tag).where(
                Tag.name == tag_data.name,
                Tag.id != tag_id
            )
        )
        if existing_name.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 태그명입니다"
            )
        
        # 태그 업데이트
        tag.name = tag_data.name
        tag.slug = slug
        
        await db.commit()
        await db.refresh(tag)
        
        logger.info(f"태그 수정됨: {tag.id} - {tag.name}")
        return TagResponse.model_validate(tag)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"태그 수정 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="태그 수정에 실패했습니다"
        )

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """태그 삭제 (로그인 필요)"""
    try:
        # 태그 조회
        query = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="태그를 찾을 수 없습니다"
            )
        
        # 해당 태그를 사용하는 게시글이 있는지 확인
        posts_query = select(func.count(post_tags.c.post_id)).where(
            post_tags.c.tag_id == tag_id
        )
        posts_result = await db.execute(posts_query)
        posts_count = posts_result.scalar()
        
        if posts_count > 0:
            # 강제 삭제 옵션이 없으면 경고
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"해당 태그를 사용하는 게시글이 {posts_count}개 있습니다. 게시글에서 태그를 먼저 제거해주세요."
            )
        
        await db.delete(tag)
        await db.commit()
        
        logger.info(f"태그 삭제됨: {tag_id} - {tag.name}")
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"태그 삭제 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="태그 삭제에 실패했습니다"
        )

@router.get("/{tag_id}/posts")
async def get_tag_posts(
    tag_id: int,
    db: AsyncSession = Depends(get_db)
):
    """특정 태그의 게시글 수 조회"""
    try:
        # 태그 존재 확인
        tag_query = select(Tag).where(Tag.id == tag_id)
        tag_result = await db.execute(tag_query)
        tag = tag_result.scalar_one_or_none()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="태그를 찾을 수 없습니다"
            )
        
        # 게시글 수 계산
        total_query = select(func.count(post_tags.c.post_id)).where(
            post_tags.c.tag_id == tag_id
        )
        
        published_query = select(func.count(post_tags.c.post_id)).select_from(
            post_tags.join(Post, post_tags.c.post_id == Post.id)
        ).where(
            post_tags.c.tag_id == tag_id,
            Post.is_published == True
        )
        
        total_result = await db.execute(total_query)
        published_result = await db.execute(published_query)
        
        total_posts = total_result.scalar()
        published_posts = published_result.scalar()
        
        return {
            "tag": TagResponse.model_validate(tag),
            "total_posts": total_posts,
            "published_posts": published_posts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"태그 게시글 통계 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="태그 게시글 통계 조회에 실패했습니다"
        ) 