import datetime
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from jose import jwt
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.templating import Jinja2Templates

from database import Base, engine

Base.metadata.create_all(bind=engine)

load_dotenv()
app = FastAPI()

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
kauth_host = "https://kauth.kakao.com"
kapi_host = "https://kapi.kakao.com"
message_template = '{"object_type":"text","text":"Hello, world!","link":{"web_url":"https://developers.kakao.com","mobile_web_url":"https://developers.kakao.com"}}'

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


def create_jwt_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.datetime.now() + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/authorize", response_class=RedirectResponse)
async def authorize(request: Request):
    scope = request.query_params.get("scope")
    scope_param = f"&scope={scope}" if scope else ""
    redirect_url = (
        f"{kauth_host}/oauth/authorize"
        f"?response_type=code&client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}{scope_param}"
    )
    return RedirectResponse(redirect_url)


@app.get("/redirect")
async def redirect(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "No code provided"}, status_code=400)
    token_url = kauth_host + "/oauth/token"
    data = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "client_secret": KAKAO_CLIENT_SECRET,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(token_url, data=data)
        token_json = token_resp.json()
        access_token = token_json.get("access_token")

        if not access_token:
            return JSONResponse({"error": "Failed to get access token", "detail": token_json}, status_code=400)

        headers = {'Authorization': f'Bearer {access_token}'}
        profile_resp = await client.get(f"{kapi_host}/v2/user/me", headers=headers)
        if profile_resp.status_code != 200:
            return JSONResponse({"error": "Failed to get user profile"}, status_code=400)

        profile_data = profile_resp.json()

        jwt_token = create_jwt_token({
            "sub": str(profile_data["id"]),
            "kakao_access_token": access_token,
            "nickname": profile_data.get("properties", {}).get("nickname", ""),
            "profile_image": profile_data.get("properties", {}).get("profile_image", "")
        })

        return RedirectResponse(url=f"/?login=success&token={jwt_token}")


@app.get("/profile")
async def profile(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jwt_token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        kakao_access_token = payload.get("kakao_access_token")

        if not kakao_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        headers = {'Authorization': f'Bearer {kakao_access_token}'}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{kapi_host}/v2/user/me", headers=headers)
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to get user profile from Kakao",
                )
            return JSONResponse(content=resp.json())
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/message")
async def message(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jwt_token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        kakao_access_token = payload.get("kakao_access_token")

        if not kakao_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        headers = {'Authorization': f'Bearer {kakao_access_token}'}
        data = {
            'template_object': message_template
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{kapi_host}/v2/api/talk/memo/default/send", headers=headers, data=data)
            return JSONResponse(content=resp.json())
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/logout")
async def logout(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jwt_token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        kakao_access_token = payload.get("kakao_access_token")

        if not kakao_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        headers = {'Authorization': f'Bearer {kakao_access_token}'}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{kapi_host}/v1/user/logout", headers=headers)
            return JSONResponse(content=resp.json())
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/unlink")
async def unlink(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jwt_token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        kakao_access_token = payload.get("kakao_access_token")

        if not kakao_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        headers = {'Authorization': f'Bearer {kakao_access_token}'}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{kapi_host}/v1/user/unlink", headers=headers)
            return JSONResponse(content=resp.json())
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
