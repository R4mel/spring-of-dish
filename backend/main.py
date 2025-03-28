from typing import Union, TypeVar, Generic

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()


class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    tags: str
    variant: Union[int, str]  # int 또는 str 허용


T = TypeVar("T")


class GenericItem(BaseModel, Generic[T]):
    name: str
    content: T


@app.post("/generic_items/")
def create_item(item: GenericItem[int]):
    return {"item": item}


@app.get("/items/{item_id}")
def read_user_item(item_id: int):
    return {"item_id": item_id}


@app.get("/items/")
def read_items(q: list[int] = Query([])):
    return {"q": q}


@app.post("/create-item/")
def create_item(item: dict[str, int]):
    return item


@app.post("/items/")
def create_item(item: Item):
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
