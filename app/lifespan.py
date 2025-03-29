from models import init_orm, close_orm
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('START')
    await init_orm()
    yield
    print('FINISH')
    await close_orm()
