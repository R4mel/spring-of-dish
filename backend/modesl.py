from sqlalchemy import Column, Integer, ForeignKey, func, VARCHAR, Table, String, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # 내부 사용자 ID
    kakao_id = Column(Integer, unique=True, nullable=False)  # 카카오에서 제공된 고유 ID
    name = Column(VARCHAR(255), nullable=True)  # 카카오에서 제공된 이름
    email = Column(VARCHAR(255), nullable=True)  # 카카오에서 제공된 이메일
    profile_image = Column(VARCHAR(255), nullable=True)  # 카카오 프로필 이미지를 저장
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    modified_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    # 사용자가 Star를 표시한 레시피와의 관계
    stars = relationship("Star", back_populates="user")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)  # 재료 ID
    name = Column(VARCHAR(255), nullable=False, index=True)  # 재료 이름
    added_date = Column(DateTime(timezone=True), nullable=False)
    limit_date = Column(DateTime(timezone=True), nullable=False)

    # 레시피와 재료 간의 다대다 관계를 설정
    recipes = relationship("Recipe", secondary="recipe_ingredient_association", back_populates="ingredients")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)  # 레시피 ID
    title = Column(VARCHAR(255), nullable=False)  # 레시피 제목
    cooking_method = Column(String, nullable=False)  # 요리 방법
    youtube_video_id = Column(VARCHAR(255), nullable=True)  # 유튜브 영상 ID
    youtube_url = Column(VARCHAR(255), nullable=True)  # 유튜브 영상 URL
    youtube_thumbnail_url = Column(VARCHAR(255), nullable=False)  # 유튜브 썸네일

    # 레시피에 필요한 재료와의 관계
    ingredients = relationship("Ingredient", secondary="recipe_ingredient_association", back_populates="recipes")

    # 사용자가 관심 표시한 정보와의 관계
    stars = relationship("Star", back_populates="recipe")


class Star(Base):
    __tablename__ = "stars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # 사용자 ID
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)  # 레시피 ID
    count = Column(Integer, nullable=False, default=0)  # 관심 표시 횟수

    # 사용자와 레시피 간의 관계
    user = relationship("User", back_populates="stars")
    recipe = relationship("Recipe", back_populates="stars")


# 레시피와 재료 간의 다대다 관계를 정의하는 중간 테이블
recipe_ingredient_association = Table(
    "recipe_ingredient_association",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True)
)
