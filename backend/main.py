import datetime
import functools
import json
import os
from typing import List, Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionMessageParam
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse, JSONResponse

from database import engine, get_db
from models import Base as SQLBase, Recipe, Ingredient, User, Star, Image
from schemas import (
    MessageResponse,
    UserResponse,
    IngredientsResponse,
    RecipeResponse,
    IngredientResponse,
    IngredientCreate,
    IngredientUpdate,
    StarResponse
)

SQLBase.metadata.create_all(bind=engine)

load_dotenv()
app = FastAPI()
# cors 설정

security = HTTPBearer()

origins = [
    "http://areono.store",
    "http://areono.store:3000",
    "http://localhost:3000",
    "http://localhost:8000"

]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
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


def create_jwt_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.datetime.now() + (expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_error_response(detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR) -> HTTPException:
    """일관된 에러 응답을 생성합니다."""
    return HTTPException(
        status_code=status_code,
        detail=detail
    )


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


def handle_db_operation(operation: str) -> Any:
    """데이터베이스 작업을 위한 데코레이터 함수"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except IntegrityError:
                raise create_error_response(
                    f"{operation} 중 중복된 데이터가 발견되었습니다",
                    status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                raise create_error_response(
                    f"{operation} 중 오류가 발생했습니다: {str(e)}"
                )

        return wrapper

    return decorator


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
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> UserResponse:
    """JWT 토큰을 검증하고 데이터베이스에서 사용자 정보를 조회합니다."""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        kakao_id = int(payload["sub"].strip("'"))

        user = db.query(User).filter(User.kakao_id == kakao_id).first()
        if not user:
            raise create_error_response("User not found", status.HTTP_401_UNAUTHORIZED)

        return UserResponse(
            kakao_id=int(getattr(user, "kakao_id")),
            nickname=str(getattr(user, "nickname")),
            profile_image=str(getattr(user, "profile_image")),
            created_at=getattr(user, "created_at")
        )
    except JWTError:
        raise create_error_response("Invalid token", status.HTTP_401_UNAUTHORIZED)


async def call_kakao_api(endpoint: str, method: str = "POST", data: dict = None) -> dict:
    """카카오 API를 호출합니다."""
    try:
        async with http_client as ac:
            response = await ac.request(
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


@app.get("/", response_class=RedirectResponse)
async def root():
    """루트 경로 접속 시 카카오 로그인 페이지로 리다이렉트"""
    return RedirectResponse(url="/authorize")


@app.get("/authorize", response_class=RedirectResponse)
async def authorize(request: Request) -> RedirectResponse:
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
@handle_db_operation("로그인")
async def redirect(request: Request, db: Session = Depends(get_db)) -> JSONResponse:
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

    async with httpx.AsyncClient() as ac:
        token_resp = await ac.post(token_url, data=data)
        token_json = token_resp.json()
        access_token = token_json.get("access_token")

        if not access_token:
            return JSONResponse({"error": "Failed to get access token", "detail": token_json}, status_code=400)

        headers = {'Authorization': f'Bearer {access_token}'}
        profile_resp = await ac.get(f"{kapi_host}/v2/user/me", headers=headers)
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
        
        return JSONResponse(content={"token": jwt_token}, status_code=200)


@app.get("/profile", response_model=UserResponse)
async def profile(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """사용자 프로필 정보를 조회합니다."""
    return current_user


@app.post("/logout", response_model=MessageResponse)
async def logout(request: Request):
    jwt_token = await get_jwt_token(request)
    payload = await validate_jwt_token(jwt_token)
    data = {'kakao_access_token': payload.get('kakao_access_token')}

    await call_kakao_api("/v1/user/logout", data=data)

    response = create_json_response({"message": "Logged out successfully"})
    return delete_jwt_cookie(response)


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


@app.get("/user-ingredients", response_model=IngredientsResponse)
@handle_db_operation("재료 조회")
async def get_user_ingredients(
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> IngredientsResponse:
    """사용자의 재료 목록을 조회합니다."""
    ingredients = db.query(Ingredient).filter(
        Ingredient.kakao_id == current_user.kakao_id,
        Ingredient.added_date <= datetime.datetime.now(),
        Ingredient.limit_date >= datetime.datetime.now()
    ).all()

    return IngredientsResponse(
        ingredients=[ingredient.to_dict() for ingredient in ingredients]
    )


@app.post("/ingredients", response_model=IngredientResponse)
@handle_db_operation("재료 추가")
async def add_ingredient(
        ingredient: IngredientCreate,
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> IngredientResponse:
    """새로운 재료를 추가합니다."""
    try:
        # 재료 이름으로 이미지 찾기
        image = db.query(Image).filter(Image.name == ingredient.name).first()

        new_ingredient = Ingredient.create(
            db=db,
            name=ingredient.name,
            category=ingredient.category,
            added_date=ingredient.added_date,
            kakao_id=current_user.kakao_id,
            image_name=image.name if image else None
        )
        db.commit()
        db.refresh(new_ingredient)

        return IngredientResponse(
            id=int(getattr(new_ingredient, "id")),
            name=str(getattr(new_ingredient, "name")),
            category=str(getattr(new_ingredient, "category")),
            added_date=getattr(new_ingredient, "added_date"),
            limit_date=getattr(new_ingredient, "limit_date"),
            is_expired=bool(getattr(new_ingredient, "is_expired")),
            days_until_expiry=int(getattr(new_ingredient, "days_until_expiry")),
            image_url=new_ingredient.image.image_url if new_ingredient.image else None
        )
    except Exception as e:
        db.rollback()
        raise create_error_response(
            f"재료 추가 중 오류가 발생했습니다: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
@handle_db_operation("재료 수정")
async def update_ingredient(
        ingredient_id: int,
        ingredient: IngredientUpdate,
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> IngredientResponse:
    """재료 정보를 수정합니다."""
    db_ingredient = db.query(Ingredient).filter(
        Ingredient.id == ingredient_id,
        Ingredient.kakao_id == current_user.kakao_id
    ).first()

    if not db_ingredient:
        raise create_error_response("재료를 찾을 수 없습니다", status.HTTP_404_NOT_FOUND)

    # 이미지 이름이 제공된 경우 해당 이미지가 존재하는지 확인
    if ingredient.image_name is not None:
        image = db.query(Image).filter(Image.name == ingredient.image_name).first()
        if not image:
            raise create_error_response(
                f"이미지 '{ingredient.image_name}'을 찾을 수 없습니다",
                status.HTTP_400_BAD_REQUEST
            )
        db_ingredient.image_name = ingredient.image_name

    if ingredient.name is not None:
        db_ingredient.name = ingredient.name
    if ingredient.category is not None:
        db_ingredient.category = ingredient.category
    if ingredient.limit_date is not None:
        db_ingredient.limit_date = ingredient.limit_date

    db.commit()
    db.refresh(db_ingredient)

    return IngredientResponse(
        id=int(getattr(ingredient, "id")),
        name=str(getattr(ingredient, "name")),
        category=str(getattr(ingredient, "category")),
        added_date=getattr(ingredient, "added_date"),
        limit_date=getattr(ingredient, "limit_date"),
        is_expired=bool(getattr(ingredient, "is_expired")),
        days_until_expiry=int(getattr(ingredient, "days_until_expiry")),
        image_url=db_ingredient.image.image_url if db_ingredient.image else None
    )


@app.delete("/ingredients/{ingredient_id}", response_model=MessageResponse)
@handle_db_operation("재료 삭제")
async def delete_ingredient(
        ingredient_id: int,
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> MessageResponse:
    """재료를 삭제합니다."""
    db_ingredient = db.query(Ingredient).filter(
        Ingredient.id == ingredient_id,
        Ingredient.kakao_id == current_user.kakao_id
    ).first()

    if not db_ingredient:
        raise create_error_response("재료를 찾을 수 없습니다", status.HTTP_404_NOT_FOUND)

    db.delete(db_ingredient)
    db.commit()

    return MessageResponse(message="재료가 삭제되었습니다")


@app.get("/recipes", response_model=List[RecipeResponse])
@handle_db_operation("레시피 조회")
async def get_recipes(
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> List[RecipeResponse]:
    """사용자가 좋아요를 누른 레시피 목록을 조회합니다."""
    recipes = db.query(Recipe).join(Star).filter(
        Star.kakao_id == current_user.kakao_id
    ).all()

    recipe_list = [
        RecipeResponse(
            id=int(getattr(recipe, "id")),
            title=str(getattr(recipe, "title")),
            subtitle=str(getattr(recipe, "subtitle")),
            youtube_link=str(getattr(recipe, "youtube_link")),
            steps=getattr(recipe, "steps"),
            ingredients=getattr(recipe, "ingredients"),
            seasonings=getattr(recipe, "seasonings"),
            created_at=getattr(recipe, "created_at")
        )
        for recipe in recipes
    ]
    return recipe_list


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
@handle_db_operation("레시피 조회")
async def get_recipe_detail(recipe_id: int, db: Session = Depends(get_db)) -> RecipeResponse:
    """특정 레시피의 상세 정보를 조회합니다."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise create_error_response("레시피를 찾을 수 없습니다", status.HTTP_404_NOT_FOUND)

    return RecipeResponse(
        id=int(getattr(recipe, "id")),
        title=str(getattr(recipe, "title")),
        subtitle=str(getattr(recipe, "subtitle")),
        youtube_link=str(getattr(recipe, "youtube_link")),
        steps=getattr(recipe, "steps"),
        ingredients=getattr(recipe, "ingredients"),
        seasonings=getattr(recipe, "seasonings"),
        created_at=getattr(recipe, "created_at")
    )


@app.post("/recipes/{recipe_id}/star", response_model=StarResponse)
@handle_db_operation("좋아요 처리")
async def toggle_star(
        recipe_id: int,
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> StarResponse:
    """레시피에 좋아요를 토글합니다."""
    try:
        # 레시피가 존재하는지 확인
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise create_error_response("레시피를 찾을 수 없습니다", status.HTTP_404_NOT_FOUND)

        # 이미 좋아요를 눌렀는지 확인
        existing_star = db.query(Star).filter(
            Star.recipe_id == recipe.id,
            Star.kakao_id == current_user.kakao_id
        ).first()

        if existing_star:
            # 좋아요 취소
            star_data = StarResponse(
                recipe_id=int(getattr(existing_star, "recipe_id")),
                kakao_id=int(getattr(existing_star, "kakao_id")),
                created_at=getattr(existing_star, "created_at")
            )
            db.delete(existing_star)
            db.commit()
            return star_data
        else:
            # 좋아요 추가
            new_star = Star(
                recipe_id=int(getattr(recipe, "id")),
                kakao_id=current_user.kakao_id,
                created_at=datetime.datetime.now()
            )
            db.add(new_star)
            try:
                db.commit()
                db.refresh(new_star)
                return StarResponse(
                    recipe_id=int(getattr(new_star, "recipe_id")),
                    kakao_id=int(getattr(new_star, "kakao_id")),
                    created_at=getattr(new_star, "created_at")
                )
            except IntegrityError:
                db.rollback()
                raise create_error_response("이미 좋아요를 누른 레시피입니다", status.HTTP_400_BAD_REQUEST)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise create_error_response(f"좋아요 처리 중 오류가 발생했습니다: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)


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

        async with http_client as ac:
            response = await ac.get(url, params=params)
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
@handle_db_operation("레시피 생성")
async def generate_recipe(
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """사용자의 보유 재료로 레시피를 생성합니다."""
    try:
        # 사용자의 재료 목록 조회
        user_ingredients = db.query(Ingredient).filter(
            Ingredient.kakao_id == current_user.kakao_id,
            Ingredient.added_date <= datetime.datetime.now(),
            Ingredient.limit_date >= datetime.datetime.now()
        ).all()

        if not user_ingredients:
            raise create_error_response(
                "사용 가능한 재료가 없습니다. 재료를 먼저 추가해주세요.",
                status.HTTP_400_BAD_REQUEST
            )

        # 사용자의 재료 이름 목록 (InstrumentedAttribute를 문자열로 변환)
        ingredient_names = [str(getattr(ing, "name")) for ing in user_ingredients]

        # GPT API 호출하여 레시피 생성
        recipe_data = await generate_recipe_with_gpt(ingredient_names)

        # 생성된 레시피를 데이터베이스에 저장
        new_recipe = Recipe(
            title=recipe_data["title"],
            subtitle=recipe_data["subtitle"],
            youtube_link=recipe_data["youtube_link"],
            steps=recipe_data["steps"],
            ingredients=recipe_data["ingredients"],
            seasonings=recipe_data["seasonings"],
            created_at=datetime.datetime.now()
        )
        db.add(new_recipe)
        db.commit()
        db.refresh(new_recipe)

        # 응답에 레시피 ID 포함
        return {
            **recipe_data,
            "id": new_recipe.id,
            "is_starred": False
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise create_error_response(
            f"레시피 생성 중 오류가 발생했습니다: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
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

        system_message: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": "당신은 요리 전문가입니다. 주어진 재료로 만들 수 있는 맛있는 요리 레시피를 제안해주세요."
        }
        user_message: ChatCompletionUserMessageParam = {
            "role": "user",
            "content": prompt
        }
        messages: List[ChatCompletionMessageParam] = [system_message, user_message]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
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
        raise create_error_response("GPT API 응답을 파싱할 수 없습니다.", status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        raise create_error_response(f"레시피 생성 중 오류가 발생했습니다: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
