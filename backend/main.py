import datetime
import json
import os
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from openai import OpenAI
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse, JSONResponse

from database import engine, get_db
from models import Base as SQLBase, Recipe, Ingredient, User, Star
from schemas import (
    MessageResponse,
    UserResponse,
    IngredientsResponse,
    RecipeResponse,
    RecipeCreate,
    IngredientResponse,
    IngredientCreate,
    IngredientUpdate
)

SQLBase.metadata.create_all(bind=engine)

load_dotenv()
app = FastAPI()

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

http_client = httpx.AsyncClient()

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
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


async def get_jwt_token(request: Request) -> str:
    """JWT 토큰을 요청 헤더에서 추출합니다."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_header.split(" ")[1]


async def validate_jwt_token(jwt_token: str) -> dict:
    """JWT 토큰을 검증하고 payload를 반환합니다."""
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        kakao_access_token = payload.get("kakao_access_token")
        if not kakao_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return payload
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def call_kakao_api(endpoint: str, method: str = "POST", data: dict = None) -> dict:
    """카카오 API를 호출합니다."""
    try:
        async with http_client as client:
            response = await client.request(
                method=method,
                url=f"{kapi_host}{endpoint}",
                headers={"Authorization": f"Bearer {data.get('kakao_access_token')}"},
                data=data
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kakao API 호출 중 오류가 발생했습니다: {str(e)}"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                           db: Session = Depends(get_db)):
    """JWT 토큰을 검증하고 데이터베이스에서 사용자 정보를 조회합니다."""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        kakao_id = int(payload["sub"].strip("'"))

        user = db.query(User).filter(User.kakao_id == kakao_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "kakao_id": user.kakao_id,
            "nickname": user.nickname,
            "profile_image": user.profile_image,
            "kakao_access_token": payload.get("kakao_access_token", "")
        }
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_jwt_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.datetime.now() + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.get("/")
async def root():
    """루트 경로 접속 시 카카오 로그인 페이지로 리다이렉트"""
    return RedirectResponse(url="/authorize")


@app.get("/authorize", response_class=RedirectResponse)
async def authorize(request: Request):
    """카카오 로그인 페이지로 리다이렉트"""
    scope = request.query_params.get("scope")
    scope_param = f"&scope={scope}" if scope else ""

    redirect_url = (
        f"{kauth_host}/oauth/authorize"
        f"?response_type=code"
        f"&client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        f"{scope_param}"
    )
    return RedirectResponse(redirect_url)


@app.get("/redirect")
async def redirect(request: Request, db: Session = Depends(get_db)):
    """카카오 로그인 콜백 처리"""
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
        kakao_id = profile_data["id"]
        nickname = profile_data.get("properties", {}).get("nickname", "")
        profile_image = profile_data.get("properties", {}).get("profile_image", "")

        # 사용자 정보 저장 또는 업데이트
        user = db.query(User).filter(User.kakao_id == kakao_id).first()
        if user:
            # 기존 사용자의 경우 닉네임과 프로필 이미지만 업데이트
            user.nickname = nickname
            user.profile_image = profile_image
        else:
            # 새로운 사용자의 경우 created_at 포함하여 생성
            user = User(
                kakao_id=kakao_id,
                nickname=nickname,
                profile_image=profile_image,
                created_at=datetime.datetime.now()
            )
            db.add(user)
        db.commit()

        jwt_token = create_jwt_token({
            "sub": repr(kakao_id),
            "kakao_access_token": access_token,
            "nickname": nickname,
            "profile_image": profile_image
        })

        # # JWT 토큰을 쿠키에 저장
        # response = RedirectResponse(url="/")
        # response.set_cookie(
        #     key="jwt_token",
        #     value=jwt_token,
        #     httponly=True,  # JavaScript에서 접근 불가
        #     secure=True,  # HTTPS에서만 전송
        #     samesite="lax",  # CSRF 방지
        #     max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 토큰 만료 시간과 동일하게 설정
        # )
        # return response

        # JWT 토큰을 응답에 포함
        return JSONResponse({
            "message": "Login successful",
            "jwt_token": jwt_token,
            "user": {
                "kakao_id": kakao_id,
                "nickname": nickname,
                "profile_image": profile_image
            }
        })


@app.get("/profile", response_model=UserResponse)
async def profile(current_user: dict = Depends(get_current_user)):
    return current_user


def create_json_response(content: dict, status_code: int = 200) -> JSONResponse:
    """JSON 응답을 생성합니다."""
    return JSONResponse(content=content, status_code=status_code)


def delete_jwt_cookie(response: JSONResponse) -> JSONResponse:
    """JWT 쿠키를 삭제합니다."""
    response.delete_cookie(
        key="jwt_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return response


@app.get("/message")
async def message(request: Request):
    jwt_token = await get_jwt_token(request)
    payload = await validate_jwt_token(jwt_token)
    data = {
        'template_object': message_template,
        'kakao_access_token': payload.get('kakao_access_token')
    }
    return await call_kakao_api("/v2/api/talk/memo/default/send", data=data)


@app.post("/logout", response_model=MessageResponse)
async def logout(request: Request):
    jwt_token = await get_jwt_token(request)
    payload = await validate_jwt_token(jwt_token)
    data = {'kakao_access_token': payload.get('kakao_access_token')}

    await call_kakao_api("/v1/user/logout", data=data)

    response = create_json_response({"message": "Logged out successfully"})
    return delete_jwt_cookie(response)


def create_error_response(detail: str, status_code: int = 500) -> HTTPException:
    """HTTP 예외를 생성합니다."""
    return HTTPException(
        status_code=status_code,
        detail=detail
    )


def get_user_by_kakao_id(db: Session, kakao_id: int) -> Optional[User]:
    """카카오 ID로 사용자를 조회합니다."""
    return db.query(User).filter(User.kakao_id == kakao_id).first()


def get_recipe_by_id(db: Session, recipe_id: int) -> Optional[Recipe]:
    """레시피 ID로 레시피를 조회합니다."""
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()


def get_star_by_recipe_and_user(db: Session, recipe_id: int, kakao_id: int) -> Optional[Star]:
    """레시피와 사용자로 좋아요를 조회합니다."""
    return db.query(Star).filter(
        Star.recipe_id == recipe_id,
        Star.kakao_id == kakao_id
    ).first()


@app.get("/user-ingredients", response_model=IngredientsResponse)
async def get_user_ingredients(
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """사용자의 재료 목록을 조회합니다."""
    try:
        ingredients = db.query(Ingredient).filter(
            Ingredient.kakao_id == current_user["kakao_id"],
            Ingredient.added_date <= datetime.datetime.now(),
            Ingredient.limit_date >= datetime.datetime.now()
        ).all()

        ingredient_list = [
            IngredientResponse(
                id=ing.id,
                name=ing.name,
                quantity=ing.quantity,
                category=ing.category,
                added_date=ing.added_date,
                limit_date=ing.limit_date,
                is_expired=ing.is_expired(),
                days_until_expiry=ing.days_until_expiry()
            )
            for ing in ingredients
        ]
        return IngredientsResponse(ingredients=ingredient_list)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"재료 조회 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/recipes/{recipe_id}/star")
async def toggle_star(
        recipe_id: int,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """레시피에 좋아요를 토글합니다."""
    try:
        # 레시피가 존재하는지 확인
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="레시피를 찾을 수 없습니다"
            )

        # 이미 좋아요를 눌렀는지 확인
        existing_star = db.query(Star).filter(
            Star.recipe_id == recipe_id,
            Star.kakao_id == current_user["kakao_id"]
        ).first()

        if existing_star:
            # 좋아요 취소
            db.delete(existing_star)
            db.commit()
            return {"message": "좋아요가 취소되었습니다"}
        else:
            # 좋아요 추가
            new_star = Star(
                recipe_id=recipe_id,
                kakao_id=current_user["kakao_id"]
            )
            db.add(new_star)
            try:
                db.commit()
                return {"message": "좋아요가 추가되었습니다"}
            except IntegrityError:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 좋아요를 누른 레시피입니다"
                )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"좋아요 처리 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/unlink", response_model=MessageResponse)
async def unlink(request: Request, db: Session = Depends(get_db)):
    jwt_token = await get_jwt_token(request)
    payload = await validate_jwt_token(jwt_token)
    data = {'kakao_access_token': payload.get('kakao_access_token')}

    await call_kakao_api("/v1/user/unlink", data=data)

    # 사용자 데이터 삭제
    user = db.query(User).filter(User.kakao_id == int(payload["sub"].strip("'"))).first()
    if user:
        db.delete(user)
        db.commit()

    response = create_json_response({"message": "Account unlinked successfully"})
    return delete_jwt_cookie(response)


async def search_youtube_video(query: str) -> str:
    """YouTube API를 사용하여 요리 영상을 비동기로 검색합니다."""
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoCategoryId": "26",
            "maxResults": 1,
            "key": YOUTUBE_API_KEY
        }

        async with http_client as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                video_id = data["items"][0]["id"]["videoId"]
                return f"https://www.youtube.com/watch?v={video_id}"

            # 검색 결과가 없거나 API 호출이 실패한 경우 검색 결과 페이지 링크 반환
            return f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    except Exception as e:
        print(f"YouTube API Error: {str(e)}")
        # 에러 발생 시에도 검색 결과 페이지 링크 반환
        return f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"


@app.post("/generate-recipe")
async def generate_recipe(ingredients: List[str]):
    """사용자의 재료로 레시피를 생성합니다."""
    try:
        # GPT API 호출하여 레시피 생성
        recipe = await generate_recipe_with_gpt(ingredients)
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-recipe", response_model=RecipeResponse)
async def save_recipe(recipe: RecipeCreate, current_user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    """사용자가 마음에 든 레시피를 저장합니다."""
    try:
        new_recipe = Recipe(
            title=recipe.title,
            subtitle=recipe.subtitle,
            youtube_link=recipe.youtube_link,
            steps=recipe.steps,
            ingredients=recipe.ingredients,
            seasonings=recipe.seasonings
        )
        db.add(new_recipe)
        db.commit()
        db.refresh(new_recipe)
        return new_recipe
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"레시피 저장 중 오류가 발생했습니다: {str(e)}"
        )


async def generate_recipe_with_gpt(ingredients: List[str]):
    """GPT API를 사용하여 레시피를 생성하고 YouTube API로 관련 영상을 검색합니다."""
    try:
        ingredient_str = ", ".join(ingredients)
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
        youtube_link = await search_youtube_video(youtube_query)

        return {
            "title": recipe_data["title"],
            "subtitle": recipe_data["subtitle"],
            "youtube_link": youtube_link,
            "steps": recipe_data["steps"],
            "ingredients": recipe_data["ingredients"],
            "seasonings": recipe_data["seasonings"]
        }
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GPT API 응답을 파싱할 수 없습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"레시피 생성 중 오류가 발생했습니다: {str(e)}"
        )


@app.get("/recipes", response_model=List[RecipeResponse])
async def get_recipes(
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """사용자가 좋아요를 누른 레시피 목록을 조회합니다."""
    try:
        recipes = db.query(Recipe).join(Star).filter(
            Star.kakao_id == current_user["kakao_id"]
        ).all()
        return recipes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"레시피 조회 중 오류가 발생했습니다: {str(e)}"
        )


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_detail(
        recipe_id: int,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """특정 레시피의 상세 정보를 조회합니다."""
    try:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="레시피를 찾을 수 없습니다"
            )
        return recipe
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"레시피 조회 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/ingredients", response_model=IngredientResponse)
async def add_ingredient(
        ingredient: IngredientCreate,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """새로운 재료를 추가합니다."""
    try:
        new_ingredient = Ingredient(
            kakao_id=current_user["kakao_id"],
            name=ingredient.name,
            quantity=ingredient.quantity,
            category=ingredient.category,
            limit_date=ingredient.limit_date
        )
        db.add(new_ingredient)
        db.commit()
        db.refresh(new_ingredient)
        return new_ingredient
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"재료 추가 중 오류가 발생했습니다: {str(e)}"
        )


@app.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
async def update_ingredient(
        ingredient_id: int,
        ingredient: IngredientUpdate,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """기존 재료 정보를 수정합니다."""
    try:
        existing_ingredient = db.query(Ingredient).filter(
            Ingredient.id == ingredient_id,
            Ingredient.kakao_id == current_user["kakao_id"]
        ).first()
        if not existing_ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="재료를 찾을 수 없습니다"
            )

        for key, value in ingredient.dict(exclude_unset=True).items():
            setattr(existing_ingredient, key, value)
        db.commit()
        db.refresh(existing_ingredient)
        return existing_ingredient
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"재료 수정 중 오류가 발생했습니다: {str(e)}"
        )


@app.delete("/ingredients/{ingredient_id}", response_model=MessageResponse)
async def delete_ingredient(
        ingredient_id: int,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """재료를 삭제합니다."""
    try:
        ingredient = db.query(Ingredient).filter(
            Ingredient.id == ingredient_id,
            Ingredient.kakao_id == current_user["kakao_id"]
        ).first()
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="재료를 찾을 수 없습니다"
            )

        db.delete(ingredient)
        db.commit()
        return {"message": "재료가 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"재료 삭제 중 오류가 발생했습니다: {str(e)}"
        )
