from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessageResponse(BaseSchema):
    message: str


class ErrorResponse(BaseSchema):
    detail: str


class UserResponse(BaseSchema):
    kakao_id: int
    nickname: str
    profile_image: str
    created_at: datetime


class IngredientCreate(BaseSchema):
    name: str
    category: str
    added_date: datetime


class IngredientUpdate(BaseSchema):
    name: Optional[str] = None
    category: Optional[str] = None
    limit_date: Optional[datetime] = None


class IngredientResponse(BaseSchema):
    id: int
    name: str
    category: str
    added_date: datetime
    limit_date: datetime
    is_expired: bool
    days_until_expiry: int


class IngredientsResponse(BaseSchema):
    ingredients: List[IngredientResponse]


class RecipeBase(BaseSchema):
    title: str = Field(..., max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    youtube_link: str
    steps: List[str]  # 요리 단계
    ingredients: List[str]  # 재료 목록
    seasonings: List[str]  # 양념 목록


class RecipeCreate(RecipeBase):
    pass


class RecipeResponse(RecipeBase):
    id: int
    created_at: datetime


class StarResponse(BaseSchema):
    recipe_id: int
    kakao_id: int
    created_at: datetime


class StarBase(BaseModel):
    kakao_id: int
    recipe_id: int


class StarCreate(StarBase):
    pass
