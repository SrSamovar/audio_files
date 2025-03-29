from datetime import timedelta
import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from crud import create_access_token
from lifespan import lifespan
from dependency import SessionDependency
from models import User
import os

app = FastAPI(
    title="Audio storage API",
    description="API for managing audio files",
    version="1.0.0",
    lifespan=lifespan()
)

# Конфигурация
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30
YANDEX_CLIENT_ID = os.getenv('YANDEX_CLIENT_ID')
YANDEX_CLIENT_SECRET = os.getenv('YANDEX_CLIENT_SECRET')
YANDEX_REDIRECT_URI = "http://localhost:8000/auth/yandex/callback"
YANDEX_OAUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"

@app.get("/auth/yandex")
async def auth_yandex():
    redirect_uri = f"{YANDEX_OAUTH_URL}?response_type=code&client_id={YANDEX_CLIENT_ID}&redirect_uri={YANDEX_REDIRECT_URI}"
    return RedirectResponse(url=redirect_uri)


@app.get("/auth/yandex/callback")
async def auth_yandex_callback(code: str, session: SessionDependency):
    # Получение токена
    token_response = requests.post(YANDEX_TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': YANDEX_CLIENT_ID,
        'client_secret': YANDEX_CLIENT_SECRET,
        'redirect_uri': YANDEX_REDIRECT_URI,
    })

    if token_response.status_code != 200:
        raise HTTPException(status_code=token_response.status_code, detail="Failed to get token")

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    # Получение информации о пользователе
    user_info_response = requests.get("https://login.yandex.ru/info", headers={
        "Authorization": f"OAuth {access_token}"
    })

    if user_info_response.status_code != 200:
        raise HTTPException(status_code=user_info_response.status_code, detail="Failed to get user info")

    user_info = user_info_response.json()

    # Сохранение информации о пользователе в базе данных
    user = session.query(User).filter(User.yandex_id == user_info['id']).first()

    if not user:
        user = User(
            yandex_id=user_info['id'],
            name=user_info.get('first_name', ''),
            email=user_info.get('default_email', '')
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    # Создание JWT-токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = create_access_token(data={"sub": user.yandex_id}, expires_delta=access_token_expires)

    return {"access_token": jwt_token, "token_type": "bearer"}
