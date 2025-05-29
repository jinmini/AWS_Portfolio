from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.post import PostType
from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse

# 게시글 기본 스키마
class PostBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    post_type: PostType
    category_id: Optional[int] = None
    is_published: bool = False

# 게시글 생성 스키마
class PostCreate(PostBase):
    tag_ids: Optional[List[int]] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "FastAPI로 마이크로서비스 구축하기",
                "content": "# FastAPI 마이크로서비스 아키텍처\n\nFastAPI는...",
                "summary": "FastAPI를 사용한 마이크로서비스 아키텍처 구축 가이드",
                "post_type": "dev",
                "category_id": 2,
                "is_published": True,
                "tag_ids": [4, 5, 6]
            }
        }

# 게시글 수정 스키마
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    post_type: Optional[PostType] = None
    category_id: Optional[int] = None
    is_published: Optional[bool] = None
    tag_ids: Optional[List[int]] = None

# 게시글 목록용 간단 스키마
class PostSummary(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    slug: str
    post_type: PostType
    is_published: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True

# 게시글 상세 응답 스키마
class PostResponse(PostSummary):
    content: str
    author_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# 게시글 목록 응답 (페이지네이션)
class PostListResponse(BaseModel):
    posts: List[PostSummary]
    total: int
    page: int
    size: int
    total_pages: int 