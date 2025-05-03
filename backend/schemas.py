from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class RecipeBase(BaseModel):
    title: str = Field(..., max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    youtube_link: str
    steps: List[str]  # 요리 단계
    ingredients: List[Dict[str, str]]  # 재료 목록 (name, iconUrl)
    seasonings: List[Dict[str, str]]  # 양념 목록 (name, iconUrl)


class RecipeCreate(RecipeBase):
    pass


class RecipeResponse(RecipeBase):
    id: int
    created_at: datetime
    is_saved: bool = False
    saved_by: Optional[int] = None

    class Config:
        orm_mode = True


class StarBase(BaseModel):
    kakao_id: int
    recipe_id: int


class StarCreate(StarBase):
    pass


class StarResponse(StarBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
