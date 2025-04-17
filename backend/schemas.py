from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    kakao_id: int
    name: str = Field(..., max_length=255)
    email: EmailStr
    profile_image: Optional[HttpUrl] = None
    created_at: datetime
    modified_at: Optional[datetime] = None


class UserCreate(UserBase):
    kakao_id: int  # 필수 필드


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True  # SQLAlchemy 모델을 기반으로 Pydantic를 사용하기 위해 설정


class IngredientBase(BaseModel):
    name: str = Field(..., max_length=255)  # 필수 필드
    added_date: datetime
    limit_date: datetime


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: int

    class Config:
        orm_mode = True


class RecipeBase(BaseModel):
    title: str = Field(..., max_length=255)  # 필수 필드
    cooking_method: str = Field(..., max_length=1024)  # 기본값은 없음
    youtube_video_id: str = Field(..., max_length=255)
    youtube_url: HttpUrl
    youtube_thumbnail_url: HttpUrl


class RecipeCreate(RecipeBase):
    ingredient_ids: List[int]  # 새로운 레시피를 생성할 때 포함된 재료들의 ID


class RecipeResponse(RecipeBase):
    id: int
    ingredients: List[IngredientResponse]

    class Config:
        orm_mode = True


class StarBase(BaseModel):
    user_id: int
    recipe_id: int
    count: int = Field(0, ge=0)  # 기본값: 0, 최소값: 0


class StarCreate(StarBase):
    pass


class StarResponse(StarBase):
    id: int

    class Config:
        orm_mode = True
