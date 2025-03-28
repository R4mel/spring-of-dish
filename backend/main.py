from fastapi import FastAPI, Query, Body, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str = None
    price: float


def get_item_from_db(item_id):
    return {
        "name": "Simple Item",
        "description": "A simple item description",
        "price": 50.0,
        "dis_price": 45.0
    }


@app.get("/items/{item_id}", response_model=Item)  # response_model: 데이터 검증, 자동 문서 생성, 보안
def read_item(item_id: int):
    try:
        if item_id < 0:
            raise ValueError("음수는 허용되지 않습니다.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return get_item_from_db(item_id)


@app.get("/users/")
def read_users(q: str = Query(None, max_length=50)):  # URL에서 ? 뒤에 오는 키-값 쌍으로 이루어진 문자열
    return {"q": q}


@app.get("/items/")
def read_items(item_id: int = Query(...)):  # ... 은 해당 필드가 필수라는 뜻
    return {"item_id": item_id}


@app.post("/items/")
def create_item(item: dict = Body(...)):
    return {"item": item}


@app.post("/advanced_items/")
def create_advanced_item(
        item: dict = Body(default=None, example={"key": "value"}, media_type="application/json",
                          alias="item_alias",
                          title="Sample Item", description="This is a sample item", deprecated=False)):
    return {"item": item}

# import os
#
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from openai import OpenAI
# from pydantic import BaseModel
#
# client = OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )
#
# app = FastAPI()
#
# # CORS 설정
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
#
# class InputIngredients(BaseModel):
#     text: str
#
#
# def HowToCook(text):
#     response = client.responses.create(
#         model="gpt-4o",
#         instructions="요리 연구가의 소개",
#         input=f"{text}로 만들 수 있는 음식과 요리 방법을 알려주세요."
#     )
#
#     return response
#
#
# @app.post("/cook")
# def cook_howtocook(input_text: InputIngredients):
#     response = HowToCook(input_text.text)
#     return {"how to cook": response}
