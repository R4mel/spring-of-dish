from sqlalchemy import Column, Integer, ForeignKey, func, VARCHAR, Table, DateTime, Text, Boolean, BigInteger
from sqlalchemy.orm import relationship

from database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(VARCHAR(255), nullable=False)  # 레시피 제목
    subtitle = Column(VARCHAR(255))  # 레시피 부제목
    youtube_link = Column(VARCHAR(255), nullable=False)  # 유튜브 링크
    steps = Column(Text, nullable=False)  # 요리 단계 (JSON 형식으로 저장)
    ingredients = Column(Text, nullable=False)  # 재료 목록 (JSON 형식으로 저장)
    seasonings = Column(Text, nullable=False)  # 양념 목록 (JSON 형식으로 저장)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_saved = Column(Boolean, default=False)  # 사용자가 저장한 레시피인지 여부
    saved_by = Column(BigInteger, nullable=True)  # 저장한 사용자의 카카오 ID

    # 사용자가 관심 표시한 정보와의 관계
    stars = relationship("Star", back_populates="recipe")
    # 재료와의 관계
    ingredients_rel = relationship("Ingredient", secondary="recipe_ingredient_association", back_populates="recipes")


class Star(Base):
    __tablename__ = "stars"

    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(Integer, nullable=False, index=True)  # 카카오 ID
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)  # 레시피 ID
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # 레시피와의 관계
    recipe = relationship("Recipe", back_populates="stars")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)  # 재료 ID
    name = Column(VARCHAR(255), nullable=False, index=True)  # 재료 이름
    added_date = Column(DateTime(timezone=True), nullable=False)
    limit_date = Column(DateTime(timezone=True), nullable=False)

    # 레시피와 재료 간의 다대다 관계를 설정
    recipes = relationship("Recipe", secondary="recipe_ingredient_association", back_populates="ingredients_rel")


# 레시피와 재료 간의 다대다 관계를 정의하는 중간 테이블
recipe_ingredient_association = Table(
    "recipe_ingredient_association",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True)
)
