import datetime
import json
import os

import httpx
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from jose import jwt
from openai import OpenAI
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.templating import Jinja2Templates

from database import engine, get_db
from models import Base, Recipe, Ingredient

Base.metadata.create_all(bind=engine)

load_dotenv()
app = FastAPI()

# 응답용 Pydantic 모델
class UserOut(BaseModel):
    user_no: int
    nickname: str
    register_date: str

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    nickname: str

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
kauth_host = "https://kauth.kakao.com"
kapi_host = "https://kapi.kakao.com"
openai_host = "https://api.openai.com/v1"
message_template = '{"object_type":"text","text":"Hello, world!","link":{"web_url":"https://developers.kakao.com","mobile_web_url":"https://developers.kakao.com"}}'

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


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
            "sub": repr(profile_data["id"]),
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
        return JSONResponse(content=payload)
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


def search_youtube_video(query):
    """YouTube API를 사용하여 요리 영상을 검색합니다."""
    try:
        # YouTube Data API v3 엔드포인트
        url = "https://www.googleapis.com/youtube/v3/search"

        # 검색 파라미터 설정
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoCategoryId": "26",  # 26은 "How-to & Style" 카테고리
            "maxResults": 1,
            "key": YOUTUBE_API_KEY
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            video_id = data["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={video_id}"

        return None
    except Exception as e:
        print(f"YouTube API Error: {str(e)}")
        return None


@app.post("/generate-recipe")
async def generate_recipe(request: Request, db: Session = Depends(get_db)):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            jwt_token = auth_header.split(" ")[1]
            payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 사용자의 재료 목록 조회
        ingredients = db.query(Ingredient).filter(
            Ingredient.added_date <= datetime.datetime.now(),
            Ingredient.limit_date >= datetime.datetime.now()
        ).all()

        if not ingredients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available ingredients found"
            )

        ingredient_list = [ing.name for ing in ingredients]
        ingredient_str = ", ".join(ingredient_list)

        prompt = f"""다음 재료들을 사용한 요리 레시피를 생성해주세요:
재료: {ingredient_str}

다음 JSON 형식으로만 응답해주세요:
{{
    "title": "요리 제목",
    "subtitle": "간단한 설명",
    "steps": [
        "1단계 설명",
        "2단계 설명",
        ...
    ],
    "ingredients": [
        "필요한 재료 1",
        "필요한 재료 2",
        ...
    ],
    "seasonings": [
        "필요한 양념 1",
        "필요한 양념 2",
        ...
    ]
}}"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 요리 전문가입니다. 주어진 재료로 만들 수 있는 맛있는 요리 레시피를 제안해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        content = response.choices[0].message.content.strip()
        recipe_data = json.loads(content)

        youtube_query = f"{recipe_data['title']} 레시피"
        youtube_link = search_youtube_video(youtube_query)

        if not youtube_link:
            youtube_link = "https://www.youtube.com/results?search_query=" + youtube_query.replace(" ", "+")

        recipe = Recipe(
            title=recipe_data["title"],
            subtitle=recipe_data["subtitle"],
            youtube_link=youtube_link,
            steps=json.dumps(recipe_data["steps"]),
            seasonings=json.dumps(recipe_data["seasonings"]),
            is_saved=False,
            saved_by=None
        )

        response_data = {
            "title": recipe_data["title"],
            "subtitle": recipe_data["subtitle"],
            "youtubeLink": youtube_link,
            "steps": recipe_data["steps"],
            "ingredients": recipe_data["ingredients"],
            "seasonings": recipe_data["seasonings"]
        }

        return JSONResponse(content=response_data)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"레시피 생성 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/save-recipe")
async def save_recipe(request: Request, recipe_data: dict, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jwt_token = auth_header.split(" ")[1]
    payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
    kakao_id = int(payload["sub"].strip("'"))

    recipe = Recipe(
        title=recipe_data["title"],
        subtitle=recipe_data["subtitle"],
        youtube_link=recipe_data["youtubeLink"],
        steps=json.dumps(recipe_data["steps"]),
        ingredients=json.dumps(recipe_data["ingredients"]),
        seasonings=json.dumps(recipe_data["seasonings"]),
        is_saved=True,
        saved_by=kakao_id
    )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return JSONResponse(content={"message": "Recipe saved successfully", "recipe_id": recipe.id})
