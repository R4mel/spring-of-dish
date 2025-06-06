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
    ingredients = Column(JSON, nullable=False)  # 재료 목록
    seasonings = Column(JSON, nullable=False)  # 양념 목록
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


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR(255), nullable=False, unique=True)
    image_url = Column(VARCHAR(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "image_url": self.image_url
        }


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR(255), index=True)
    category = Column(VARCHAR(50))  # 카테고리 (예: "채소", "육류", "조미료")
    added_date = Column(DateTime, default=datetime.datetime.now)
    limit_date = Column(DateTime, nullable=False)
    kakao_id = Column(BigInteger, ForeignKey("users.kakao_id"))
    image_name = Column(VARCHAR(255), ForeignKey("images.name"), nullable=True)

    user = relationship("User", back_populates="ingredients")
    image = relationship("Image", foreign_keys=[image_name], primaryjoin="Ingredient.image_name == Image.name")

    @property
    def is_expired(self):
        return datetime.datetime.now() > self.limit_date

    @property
    def days_until_expiry(self):
        return (self.limit_date - datetime.datetime.now()).days

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "added_date": self.added_date.isoformat(),
            "limit_date": self.limit_date.isoformat(),
            "is_expired": self.is_expired,
            "days_until_expiry": self.days_until_expiry,
            "image_url": self.image.image_url if self.image else None
        }

    @classmethod
    def create(cls, db, name, category, added_date, kakao_id, image_name=None):
        ingredient = cls(
            name=name,
            category=category,
            added_date=added_date,
            limit_date=added_date + datetime.timedelta(days=15),
            kakao_id=kakao_id,
            image_name=image_name
        )
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
        return ingredient