from fastapi import FastAPI, APIRouter
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com", "localhost", "127.0.0.1"])
# APIRouter를 통한 라우트(허용된 호스트에서만 접근 가능) <-> 메인 애플리케이션을 통한 일반 라우트(모든 호스트에서 접근 가능)
router = APIRouter()


@router.get("/items/")
def read_items():
    return {"item": "apple"}


@router.get("/users/")
def read_users():
    return {"user": "John"}


app.include_router(router, prefix="/api", tags=["items"])

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
