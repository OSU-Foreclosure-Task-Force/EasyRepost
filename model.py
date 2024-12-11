from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Generic, TypeVar, Type, Optional
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from fastapi import Depends
from database import get_session

Base = declarative_base()


class BaseWithDict(Base):
    def to_dict(self) -> dict:
        """
        Convert a model instance to a dictionary.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


T = TypeVar("T", bound=Base)


class BaseCRUD(Generic[T]):
    model: Type[T]  # Declare the type of the specific model

    @classmethod
    async def get(cls, id: int, session: AsyncSession = Depends(get_session)) -> T:
        """Get the record with the specified ID"""
        statement = select(cls.model).where(cls.model.id == id)
        result = await session.execute(statement)
        instance = result.scalars().first()
        if instance is None:
            raise NoResultFound(f"No record found with ID {id}")
        return instance

    @classmethod
    async def get_multiple(cls, limit: Optional[int] = None, session: AsyncSession = Depends(get_session)) -> list[T]:
        """Get a specified number of records, default to all"""
        statement = select(cls.model)
        if limit:
            statement = statement.limit(limit)
        result = await session.execute(statement)
        return list(result.scalars().all())

    @classmethod
    async def create(cls, session: AsyncSession = Depends(get_session), **kwargs) -> T:
        """Create a new record"""
        instance = cls.model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    @classmethod
    async def update(cls, id: int, session: AsyncSession = Depends(get_session), **kwargs) -> T:
        """Update the record with the specified ID"""
        instance = await cls.get(id, session)
        if not instance:
            raise NoResultFound(f"No record found with ID {id}")

        for key, value in kwargs.items():
            setattr(instance, key, value)

        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    @classmethod
    async def delete(cls, id: int, session: AsyncSession = Depends(get_session)) -> bool:
        """Delete the record with the specified ID"""
        instance = await cls.get(id, session)
        if not instance:
            return False

        await session.delete(instance)
        await session.commit()
        return True


class Hub(BaseWithDict, BaseCRUD["Hub"]):
    __tablename__ = "hubs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, default="")
    subscription_api = Column(String, default="")
    model = "Hub"


class Subscription(BaseWithDict, BaseCRUD["Subscription"]):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hub_id = Column(Integer, ForeignKey("hubs.id"), index=True)
    topic_url = Column(String, default="")
    time = Column(DateTime, default=datetime.now())
    lease_time = Column(DateTime, default=datetime.now())
    model = "Subscription"


class DownloadTask(BaseWithDict, BaseCRUD["DownloadTask"]):
    __tablename__ = "download_tasks"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String, default=None)
    path = Column(String, default=str(Path()))
    state = Column(SAEnum(Enum), default=None)
    model = "DownloadTask"


class UploadTask(BaseWithDict, BaseCRUD["UploadTask"]):
    __tablename__ = "upload_tasks"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String, default=None)
    path = Column(String, default=str(Path()))
    state = Column(SAEnum(Enum), default=None)
    model = "UploadTask"
