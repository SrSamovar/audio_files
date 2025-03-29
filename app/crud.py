from app.auth import verify_token
from app.dependency import SessionDependency
from models import ORM_OBJ, ORM_CLS, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Request

async def add_item(session: AsyncSession, item: ORM_OBJ):
    session.add(item)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail='record already exist')


async def get_user(request: Request, user_id: int, session: SessionDependency):
    token = request.headers.get("Authorization")

    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Not authenticated")

    token = token.split(" ")[1]
    yandex_id = verify_token(token)

    if not yandex_id:
        raise HTTPException(status_code=403, detail="Invalid token")

    user = session.query(User).filter(User.yandex_id == yandex_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own profile")

    return user
