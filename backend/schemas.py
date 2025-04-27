from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    nickname: str = Field(..., max_length=100)
    kakao_id: int
    name: str = Field(..., max_length=255)
    email: EmailStr
    profile_image: Optional[HttpUrl] = None
    created_at: datetime
    modified_at: Optional[datetime] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    user_no: int
    register_date: datetime

    class Config:
        orm_mode = True


class IngredientBase(BaseModel):
    name: str = Field(..., max_length=255)
    added_date: datetime
    limit_date: datetime


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: int

    class Config:
        orm_mode = True


class RecipeBase(BaseModel):
    title: str = Field(..., max_length=255)
    cooking_method: str = Field(..., max_length=255)
    youtube_video_id: str = Field(..., max_length=255)
    youtube_url: str
    youtube_thumbnail_url: str


class RecipeCreate(RecipeBase):
    ingredient_ids: List[int]


class RecipeResponse(RecipeBase):
    id: int
    ingredients: List[IngredientResponse]

    class Config:
        orm_mode = True


class StarBase(BaseModel):
    user_no: int
    recipe_id: int
    count: int = Field(0, ge=0)


class StarCreate(StarBase):
    pass


class StarResponse(StarBase):
    id: int

    class Config:
        orm_mode = True
