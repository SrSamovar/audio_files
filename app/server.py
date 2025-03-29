from datetime import timedelta
from typing import Annotated
import requests
from app.models import AudioFile
from crud import add_item, get_user
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request, Form
from fastapi.responses import RedirectResponse
from schema import UserUpdateRequest, UserUpdateResponse, GetUserResponse, GetAudioFileResponse
from auth import verify_token, create_access_token, YANDEX_OAUTH_URL, YANDEX_CLIENT_ID, YANDEX_REDIRECT_URI, \
    YANDEX_TOKEN_URL, YANDEX_CLIENT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES
from lifespan import lifespan
from dependency import SessionDependency
from models import User
import os

app = FastAPI(
    title="Audio storage API",
    description="API for managing audio files",
    version="1.0.0",
    lifespan=lifespan
)



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


@app.post("/upload-audio")
async def upload_audio(
        session: SessionDependency,
        file: Annotated[UploadFile, File()],
        filename: Annotated[str, Form()] = None
):
    token = file.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Not authenticated")

    token = token.split(" ")[1]
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid token")

    user = session.query(User).filter(User.yandex_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if filename is None:
        filename = file.filename

    file_location = f"audio_files/{filename}"

    if os.path.exists(file_location):
        raise HTTPException(status_code=400, detail="File already exists")

    with open(file_location, "wb") as audio_file:
        audio_file.write(await file.read())

    return {"info": f"File '{filename}' uploaded successfully"}

@app.patch("/api/v1/user/{user_id}", response_model=UserUpdateResponse)
async def update_user(session: SessionDependency, user_id: int,
                      user_data: Annotated[UserUpdateRequest, Form()], request: Request):
    user = await get_user(request, user_id, session)

    user_json = user_data.model_dump(exclude_unset=True)

    for field, value in user_json.items():
        setattr(user, field, value)

    await  add_item(session, user)
    session.commit()

    return user.id_dict

@app.delete("/api/v1/user/{user_id}")
async def delete_user(session: SessionDependency, user_id: Annotated[int, Form()], request: Request):
    user = await get_user(request, user_id, session)

    if not request.user.is_superuser:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this user")

    session.delete(user)
    await session.commit()
    return {"detail": "User deleted successfully"}


@app.get('/api/v1/user/{user_id}', response_model=GetUserResponse)
async def read_user(session: SessionDependency, user_id: Annotated[int, Form()], request: Request):
    user = await get_user(request, user_id, session)
    return user.dict_

@app.get('/api/v1/user/{user_id}/audio-files', response_model=list[GetAudioFileResponse])
async def list_audio_files(session: SessionDependency, user_id: Annotated[int, Form()], request: Request):
    user = await get_user(request, user_id, session)

    audio_files = session.query(AudioFile).filter(AudioFile.user.id == user.id)

    if not audio_files:
        raise HTTPException(status_code=404, detail="No audio files found")

    return [file.dict_ for file in audio_files]
