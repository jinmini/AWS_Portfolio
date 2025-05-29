from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 댓글 기본 스키마
class CommentBase(BaseModel):
    content: str
    author_name: str
    author_email: Optional[str] = None

# 댓글 생성 스키마
class CommentCreate(CommentBase):
    post_id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "post_id": 1,
                "content": "정말 유용한 포스트네요! 감사합니다.",
                "author_name": "독자김",
                "author_email": "reader@example.com"
            }
        }

# 댓글 응답 스키마
class CommentResponse(CommentBase):
    id: int
    post_id: int
    is_approved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# 댓글 목록 응답
class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int 