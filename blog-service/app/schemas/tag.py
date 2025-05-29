from pydantic import BaseModel
from datetime import datetime

# 태그 기본 스키마
class TagBase(BaseModel):
    name: str
    slug: str

# 태그 생성 스키마
class TagCreate(TagBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "React",
                "slug": "react"
            }
        }

# 태그 응답 스키마
class TagResponse(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 