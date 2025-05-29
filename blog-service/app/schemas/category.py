from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 카테고리 기본 스키마
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

# 카테고리 생성 스키마
class CategoryCreate(CategoryBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Frontend",
                "slug": "frontend",
                "description": "프론트엔드 개발 기술"
            }
        }

# 카테고리 응답 스키마
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 