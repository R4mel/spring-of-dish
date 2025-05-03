from datetime import datetime, timedelta

from database import SessionLocal
from models import Ingredient


def add_test_ingredients():
    db = SessionLocal()
    try:
        # 기존 데이터 삭제
        db.query(Ingredient).delete()

        # 테스트 데이터 추가
        ingredients = [
            Ingredient(
                name="계란",
                added_date=datetime.now(),
                limit_date=datetime.now() + timedelta(days=14)
            ),
            Ingredient(
                name="쌀",
                added_date=datetime.now(),
                limit_date=datetime.now() + timedelta(days=180)
            ),
            Ingredient(
                name="양파",
                added_date=datetime.now(),
                limit_date=datetime.now() + timedelta(days=7)
            ),
            Ingredient(
                name="당근",
                added_date=datetime.now(),
                limit_date=datetime.now() + timedelta(days=7)
            ),
            Ingredient(
                name="감자",
                added_date=datetime.now(),
                limit_date=datetime.now() + timedelta(days=14)
            )
        ]

        db.add_all(ingredients)
        db.commit()
        print("Test ingredients added successfully!")

    except Exception as e:
        print(f"Error adding test data: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_test_ingredients()
