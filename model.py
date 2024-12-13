import enum
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy.exc import NoResultFound
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from database import get_session

Base = declarative_base()


class BaseWithUtils(Base):
    model: type[Base]

    @classmethod
    async def get(cls, id: int) -> Base:
        session = get_session()
        """Get the record with the specified ID"""
        statement = select(cls.model).where(cls.model.id == id)
        result = await session.execute(statement)
        instance = result.scalars().first()
        if instance is None:
            raise NoResultFound(f"No record found with ID {id}")
        return instance

    @classmethod
    async def get_multiple(cls, limit: Optional[int] = None) -> list[Base]:
        session = get_session()
        """Get a specified number of records, default to all"""
        statement = select(cls.model)
        if limit:
            statement = statement.limit(limit)
        result = await session.execute(statement)
        return list(result.scalars().all())

    @classmethod
    async def create(cls, **kwargs) -> Base:
        session = get_session()
        """Create a new record"""
        instance = cls.model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    @classmethod
    async def update(cls, id: int, **kwargs) -> Base:
        """Update the record with the specified ID"""
        session = get_session()
        instance = await cls.get(id)
        if not instance:
            raise NoResultFound(f"No record found with ID {id}")

        for key, value in kwargs.items():
            setattr(instance, key, value)

        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    @classmethod
    async def delete(cls, id: int) -> bool:
        """Delete the record with the specified ID"""
        session = get_session()
        instance = await cls.get(id)
        if not instance:
            return False

        await session.delete(instance)
        await session.commit()
        return True

    def to_dict(self) -> dict:
        """
        Convert a model instance to a dictionary.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Hub(BaseWithUtils):
    __tablename__ = "hubs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, default="")
    subscription_api = Column(String, default="")


Hub.model = Hub


class Subscription(BaseWithUtils):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hub_id = Column(Integer, ForeignKey("hubs.id"), index=True)
    topic_url = Column(String, default="")
    time = Column(DateTime, default=datetime.now())
    lease_time = Column(DateTime, default=datetime.now())


Subscription.model = Subscription


class TaskState(enum.Enum):
    WAITING = 1
    IN_QUEUE = 2
    PROCESSING = 3
    PAUSE = 4
    SUSPENDED = 5
    COMPLETED = 6
    FAILED = 7


class TaskPriority(enum.Enum):
    NO_HURRY = 0
    DEFAULT = 1
    IN_HURRY = 2


class Task(BaseWithUtils):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String, default=None)
    path = Column(String, default=str(Path()))
    wait_time = Column(TIMESTAMP, default=datetime.now().timestamp())
    state = Column(Enum(TaskState))
    priority = Column(Enum(TaskPriority))


class DownloadTask(Task):
    __tablename__ = "download_tasks"


DownloadTask.model = DownloadTask


class UploadTask(Task):
    __tablename__ = "upload_tasks"


UploadTask.model = UploadTask
