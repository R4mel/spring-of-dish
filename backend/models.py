import datetime

from sqlalchemy import Column, Integer, ForeignKey, func, VARCHAR, DateTime, BigInteger, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    kakao_id = Column(BigInteger, primary_key=True, index=True)
    nickname = Column(VARCHAR(255))
    profile_image = Column(VARCHAR(255))
    created_at = Column(DateTime, default=datetime.datetime.now)

    ingredients = relationship("Ingredient", back_populates="user")
    stars = relationship("Star", back_populates="user")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(VARCHAR(255), nullable=False)
    subtitle = Column(VARCHAR(255))
    youtube_link = Column(VARCHAR(255), nullable=False)
    steps = Column(JSON, nullable=False)  # 요리 단계
    ingredients = Column(JSON, nullable=False)  # 재료 목록 (name, iconUrl)
    seasonings = Column(JSON, nullable=False)  # 양념 목록 (name, iconUrl)
    created_at = Column(DateTime(timezone=True), default=func.now())

    stars = relationship("Star", back_populates="recipe")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "youtube_link": self.youtube_link,
            "steps": self.steps,
            "ingredients": self.ingredients,
            "seasonings": self.seasonings,
            "created_at": self.created_at
        }


class Star(Base):
    __tablename__ = "stars"

    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(BigInteger, ForeignKey("users.kakao_id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    recipe = relationship("Recipe", back_populates="stars")
    user = relationship("User", back_populates="stars")

    __table_args__ = (
        UniqueConstraint('recipe_id', 'kakao_id', name='uix_recipe_user'),
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR(255), index=True)
    quantity = Column(VARCHAR(50))  # 수량 (예: "2개", "300g", "1컵")
    category = Column(VARCHAR(50))  # 카테고리 (예: "채소", "육류", "조미료")
    added_date = Column(DateTime, default=datetime.datetime.now)
    limit_date = Column(DateTime)
    kakao_id = Column(BigInteger, ForeignKey("users.kakao_id"))

    user = relationship("User", back_populates="ingredients")

    def is_expired(self):
        return datetime.datetime.now() > self.limit_date

    def days_until_expiry(self):
        return (self.limit_date - datetime.datetime.now()).days

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "category": self.category,
            "added_date": self.added_date.isoformat(),
            "limit_date": self.limit_date.isoformat(),
            "is_expired": self.is_expired(),
            "days_until_expiry": self.days_until_expiry()
        }

    @classmethod
    def create(cls, db, name, quantity, category, limit_date, kakao_id):
        ingredient = cls(
            name=name,
            quantity=quantity,
            category=category,
            limit_date=limit_date,
            kakao_id=kakao_id
        )
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
        return ingredient
