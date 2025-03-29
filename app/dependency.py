import os
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Session


async def get_session() -> AsyncSession:
    with Session() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]