from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import selectinload
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate, CommentResponse, CommentListResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/post/{post_id}", response_model=CommentListResponse)
async def get_post_comments(
    post_id: int,
    approved_only: bool = Query(True, description="승인된 댓글만"),
    db: AsyncSession = Depends(get_db)
):
    """특정 게시글의 댓글 목록 조회"""
    try:
        # 게시글 존재 확인
        post_query = select(Post).where(Post.id == post_id)
        post_result = await db.execute(post_query)
        post = post_result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다"
            )
        
        # 댓글 조회
        query = select(Comment).where(Comment.post_id == post_id)
        
        if approved_only:
            query = query.where(Comment.is_approved == True)
        
        query = query.order_by(desc(Comment.created_at))
        
        result = await db.execute(query)
        comments = result.scalars().all()
        
        return CommentListResponse(
            comments=[CommentResponse.model_validate(comment) for comment in comments],
            total=len(comments)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"댓글 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 목록 조회에 실패했습니다"
        )

@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """댓글 상세 조회"""
    try:
        query = select(Comment).where(Comment.id == comment_id)
        result = await db.execute(query)
        comment = result.scalar_one_or_none()
        
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="댓글을 찾을 수 없습니다"
            )
        
        return CommentResponse.model_validate(comment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"댓글 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 조회에 실패했습니다"
        )

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db)
):
    """댓글 작성 (로그인 불필요)"""
    try:
        # 게시글 존재 확인
        post_query = select(Post).where(
            and_(
                Post.id == comment_data.post_id,
                Post.is_published == True
            )
        )
        post_result = await db.execute(post_query)
        post = post_result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없거나 발행되지 않은 게시글입니다"
            )
        
        # 댓글 생성 (기본적으로 승인 대기 상태)
        comment = Comment(
            post_id=comment_data.post_id,
            author_name=comment_data.author_name,
            author_email=comment_data.author_email,
            content=comment_data.content,
            is_approved=False  # 관리자 승인 필요
        )
        
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        
        logger.info(f"댓글 작성됨: {comment.id} - {comment.author_name}")
        return CommentResponse.model_validate(comment)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"댓글 작성 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 작성에 실패했습니다"
        )

@router.patch("/{comment_id}/approve", response_model=CommentResponse)
async def approve_comment(
    comment_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """댓글 승인 (관리자 전용)"""
    try:
        # 댓글 조회
        query = select(Comment).where(Comment.id == comment_id)
        result = await db.execute(query)
        comment = result.scalar_one_or_none()
        
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="댓글을 찾을 수 없습니다"
            )
        
        # 댓글 승인
        comment.is_approved = True
        await db.commit()
        await db.refresh(comment)
        
        logger.info(f"댓글 승인됨: {comment.id}")
        return CommentResponse.model_validate(comment)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"댓글 승인 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 승인에 실패했습니다"
        )

@router.patch("/{comment_id}/reject", response_model=CommentResponse)
async def reject_comment(
    comment_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """댓글 승인 취소 (관리자 전용)"""
    try:
        # 댓글 조회
        query = select(Comment).where(Comment.id == comment_id)
        result = await db.execute(query)
        comment = result.scalar_one_or_none()
        
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="댓글을 찾을 수 없습니다"
            )
        
        # 댓글 승인 취소
        comment.is_approved = False
        await db.commit()
        await db.refresh(comment)
        
        logger.info(f"댓글 승인 취소됨: {comment.id}")
        return CommentResponse.model_validate(comment)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"댓글 승인 취소 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 승인 취소에 실패했습니다"
        )

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """댓글 삭제 (관리자 전용)"""
    try:
        # 댓글 조회
        query = select(Comment).where(Comment.id == comment_id)
        result = await db.execute(query)
        comment = result.scalar_one_or_none()
        
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="댓글을 찾을 수 없습니다"
            )
        
        await db.delete(comment)
        await db.commit()
        
        logger.info(f"댓글 삭제됨: {comment_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"댓글 삭제 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 삭제에 실패했습니다"
        )

@router.get("/pending", response_model=CommentListResponse)
async def get_pending_comments(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """승인 대기 중인 댓글 목록 (관리자 전용)"""
    try:
        # 승인 대기 중인 댓글 조회
        query = select(Comment).options(
            selectinload(Comment.post)
        ).where(
            Comment.is_approved == False
        ).order_by(desc(Comment.created_at))
        
        result = await db.execute(query)
        comments = result.scalars().all()
        
        return CommentListResponse(
            comments=[CommentResponse.model_validate(comment) for comment in comments],
            total=len(comments)
        )
        
    except Exception as e:
        logger.error(f"승인 대기 댓글 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="승인 대기 댓글 조회에 실패했습니다"
        )

@router.get("/", response_model=CommentListResponse)
async def get_all_comments(
    approved_only: bool = Query(False, description="승인된 댓글만"),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """모든 댓글 목록 (관리자 전용)"""
    try:
        query = select(Comment).options(
            selectinload(Comment.post)
        )
        
        if approved_only:
            query = query.where(Comment.is_approved == True)
        
        query = query.order_by(desc(Comment.created_at))
        
        result = await db.execute(query)
        comments = result.scalars().all()
        
        return CommentListResponse(
            comments=[CommentResponse.model_validate(comment) for comment in comments],
            total=len(comments)
        )
        
    except Exception as e:
        logger.error(f"전체 댓글 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="전체 댓글 조회에 실패했습니다"
        ) 