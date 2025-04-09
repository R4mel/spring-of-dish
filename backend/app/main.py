from typing import Optional

from fastapi import FastAPI, Depends
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session
from starlette.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/spring_of_dish"
engine = create_engine(DATABASE_URL)
Base = declarative_base()


class Memo(Base):
    __tablename__ = "memo"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    content = sqlalchemy.Column(sqlalchemy.String)


class MemoCreate(BaseModel):
    title: str
    content: str


class MemoUpdate(BaseModel):
    title: Optional[str] = None
    str: Optional[str] = None


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)


@app.post("/memos/", response_model=Memo)
async def create_memo(memo: MemoCreate, db: Session = Depends(get_db)):
    new_memo = Memo(title=memo.title, content=memo.content)
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo)
    return {"id": new_memo.id, "title": new_memo.title, "content": new_memo.content}

# class User(Base):  # 유저 테이블
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     kakao_id = Column(String, unique=True, index=True)
#     nickname = Column(String)
#     created_at = Column(DateTime, default=datetime)
#
#     user_ingredients = relationship("UserIngredient", back_populates="user")
#
#
# class Ingredient(Base):  # 재료 테이블
#     __tablename__ = "ingredients"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True, index=True)
#     category = Column(String)
#
#     user_ingredients = relationship("UserIngredient", back_populates="ingredients")
#
#
# class UserIngredient(Base):  # 보유 재료 테이블
#     __tablename__ = "user_ingredients"
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     ingredient_id = Column(Integer, ForeignKey("ingredients.id"))
#     quantity = Column(Integer)
#     expiration_date = Column(Date)  # 소비기한
#     shelf_life = Column(Date)  # 유통기한
#     created_at = Column(DateTime, default=datetime)
#
#     user = relationship("User", back_populates="user_ingredients")
#     ingredient = relationship("Ingredient", back_populates="user_ingredients")
#
#
# class UserCreate(BaseModel):
#     kakao_id: str
#     nickname: str
#     created_at: datetime
#
#
# class IngredientCreate(BaseModel):
#     name: str
#     category: str
#
#
# class UserIngredientCreate(BaseModel):
#     user_id: int
#     ingredient_id: int
#     quantity: int = Field(..., gt=0, description="재료 개수는 1개 이상이어야 합니다.")
#     expiration_date: datetime
#     shelf_life: datetime
#
#
# # 재료 수정 요청 시 사용하는 스키마
# class UserIngredientUpdate(BaseModel):
#     quantity: Optional[int] = Field(None, gt=0)
#     expiration_date: Optional[date]
#     shelf_life: Optional[date]
#
#
# # 응답할 때 사용하는 스키마
# class UserIngredientResponse(BaseModel):
#     id: int
#     user_id: int
#     ingredient_id: int
#     quantity: int
#     expiration_date: date
#     shelf_life: date
#     created_at: datetime
#
#     class Config:
#         orm_mode = True  # SQLAlchemy 모델 -> Pydantic 자동 변환
#
#

#
# router = APIRouter(
#     prefix="/user-ingredients",
#     tags=["UserIngredient"],
# )
#
# app.include_router(router)
#
#
# # 보유 재료 추가
# @router.post("/", response_model=UserIngredientResponse)
# def create_user_ingredient(user_ingredient: UserIngredientCreate, db: Session = Depends(get_db)):
#     db_user_ingredient = UserIngredient(**user_ingredient.dict())
#     db.add(db_user_ingredient)
#     db.commit()
#     db.refresh(db_user_ingredient)
#     return db_user_ingredient
#
#
# # 특정 유저 보유 재료 목록 조회
# @router.get("/", response_model=list[UserIngredientResponse])
# def get_user_ingredients(user_id: int, db: Session = Depends(get_db)):
#     user_ingredients = db.query(UserIngredient).filter(UserIngredient.user_id == user_id).all()
#     return user_ingredients
#
#
# # 보유 재료 단건 조회
# @router.get("/{user_id}", response_model=UserIngredientResponse)
# def get_user_ingredient(user_id: int, db: Session = Depends(get_db)):
#     user_ingredient = db.query(UserIngredient).filter(UserIngredient.id == user_id).first()
#     if not user_ingredient:
#         raise HTTPException(status_code=404, detail="재료를 찾을 수 없습니다.")
#     return user_ingredient
#
#
# # 보유 재료 수정
# @router.patch("/{user_id}", response_model=UserIngredientResponse)
# def update_user_ingredient(user_id: int, update_data: UserIngredientUpdate, db: Session = Depends(get_db)):
#     user_ingredient = db.query(UserIngredient).filter(UserIngredient.id == user_id).first()
#     if not user_ingredient:
#         raise HTTPException(status_code=404, detail="재료를 찾을 수 없습니다.")
#
#     update_data = update_data.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(user_ingredient, key, value)
#
#     db.commit()
#     db.refresh(user_ingredient)
#     return user_ingredient
#
#
# # 보유 재료 삭제
# @router.delete("/{user_id}")
# def delete_user_ingredient(user_id: int, db: Session = Depends(get_db)):
#     user_ingredient = db.query(UserIngredient).filter(UserIngredient.id == user_id).first()
#     if not user_ingredient:
#         raise HTTPException(status_code=404, detail="재료를 찾을 수 없습니다.")
#
#     db.delete(user_ingredient)
#     db.commit()
#     return {"detail": "재료 삭제 완료"}
