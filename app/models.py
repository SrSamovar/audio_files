from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy import Integer, String, Boolean, DateTime, func, UUID, ForeignKey, CheckConstraint
import os

POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'LSamovar69')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'app')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5433')


DSN = (f'postgresql+asyncpg://'
       f'{POSTGRES_USER}:{POSTGRES_PASSWORD}@'
       f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')

engine = create_async_engine(DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):

    @property
    def id_dict(self):
        return {"id": self.id}


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    yandex_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    audios: Mapped[list['AudioFile']] = relationship('AudioFile', lazy='joined', back_populates='user')

    @property
    def dict_(self):
        return {
            "id": self.id,
            "yandex_id": self.yandex_id,
            "name": self.name,
            "email": self.email
        }

class AudioFile(Base):
    __tablename__ = 'audio_files'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, unique=True)
    file_path: Mapped[str] = mapped_column(String)
    user: Mapped[User] = relationship(User, lazy='joined', back_populates='audios')


ORM_OBJ = User | AudioFile
ORM_CLS = type[User] | type[AudioFile]

async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()

