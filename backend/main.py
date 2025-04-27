import os
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

from database import Base, engine

Base.metadata.create_all(bind=engine)

load_dotenv()
app = FastAPI()

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# 프론트 서버: 5500, 백엔드 서버: 8000 CORS 문제 해결
# 배포 시, allow_origins 수정 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/login/kakao")
def login_kakao():
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        f"&response_type=code"
    )
    return RedirectResponse(kakao_auth_url)


@app.get("/auth/kakao/callback")
async def kakao_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "No code provided"}, status_code=400)

    # 1. 토큰 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code,
    }
    if KAKAO_CLIENT_SECRET:
        data["client_secret"] = KAKAO_CLIENT_SECRET

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(token_url, data=data)
        token_json = token_resp.json()
        access_token = token_json.get("access_token")

        if not access_token:
            return JSONResponse({"error": "Failed to get access token", "detail": token_json}, status_code=400)

        # 2. 사용자 정보 요청
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_resp = await client.get(user_info_url, headers=headers)
        user_json = user_resp.json()

    return JSONResponse(user_json)
