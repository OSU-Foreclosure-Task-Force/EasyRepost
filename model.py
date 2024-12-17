import enum
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy.exc import NoResultFound
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, TIMESTAMP, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from database import async_session, engine
from pydantic import BaseModel, Field

Base = declarative_base()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class BaseWithUtils(Base):
    __abstract__ = True
    model: type[Base]

    @classmethod
    async def get(cls, id: int) -> Base:
        """Get the record with the specified ID"""
        async with async_session() as session:
            statement = select(cls.model).where(cls.model.id == id)
            result = await session.execute(statement)
            instance = result.scalars().first()
            if instance is None:
                raise NoResultFound(f"No record found with ID {id}")
            return instance

    @classmethod
    async def get_multiple(cls, limit: Optional[int] = None) -> list[Base]:
        """Get a specified number of records, default to all"""
        async with async_session() as session:
            statement = select(cls.model)
            if limit:
                statement = statement.limit(limit)
            result = await session.execute(statement)
            return list(result.scalars().all())

    @classmethod
    async def create(cls, **kwargs) -> Base:
        """Create a new record"""
        async with async_session() as session:
            instance = cls.model(**kwargs)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    @classmethod
    async def update(cls, id: int, **kwargs) -> Base:
        """Update the record with the specified ID"""
        async with async_session() as session:
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
        async with async_session() as session:
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


class UploaderSessionEncrypted(BaseWithUtils):
    __tablename__ = "uploader_sessions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_maker_name = Column(String, default=None)
    encrypted_configuration = Column(Text, default=None)


UploaderSessionEncrypted.model = UploaderSessionEncrypted


class Subscription(BaseWithUtils):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    site = Column(String, default=None)
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


class TaskFilter(BaseModel):
    states: frozenset[TaskState] = frozenset()
    filter_out: bool = False


class Task(BaseWithUtils):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, default=None)
    extension = Column(String, default=None)
    url = Column(String, default=None)
    path = Column(String, default=str(Path()))
    wait_time = Column(TIMESTAMP, default=datetime.now().timestamp())
    state = Column(Enum(TaskState))
    priority = Column(Enum(TaskPriority))

    @classmethod
    async def get_tasks_by_state(cls, states: frozenset[TaskState], filter_out: bool = False):
        async with async_session() as session:
            statement = select(cls).where(cls.state.in_(states))
            if filter_out:
                statement = select(cls).where(cls.state.notin_(states))
            result = await session.execute(statement)
            return result.scalars().all()

    @property
    def file_path(self) -> Path:
        return Path(str(self.path), str(self.name + self.extension))


class NewTask(BaseModel):
    name: str
    url: str
    site: str
    wait_time: int = Field(0)
    priority: int = Field(TaskPriority.DEFAULT)


class DownloadTask(Task):
    __tablename__ = "download_tasks"
    site = Column(String, default=None)
    with_description = Column(Boolean, default=True)
    with_subtitles = Column(Boolean, default=True)
    with_thumbnail = Column(Boolean, default=True)
    format = Column(String, default=None)
    resolution_x = Column(Integer, default=None)
    resolution_y = Column(Integer, default=None)
    video_codec = Column(String, default=None)
    audio_codec = Column(String, default=None)
    video_bit_rate = Column(Integer, default=None)
    audio_bit_rate = Column(Integer, default=None)
    sample_rate = Column(Integer, default=None)
    frame_rate = Column(Integer, default=None)

    @staticmethod
    async def destroy_download_task(task: "DownloadTask"):
        pass


DownloadTask.model = DownloadTask


class UploadTask(Task):
    __tablename__ = "upload_tasks"
    destination = Column(String, default=None)

    @staticmethod
    async def destroy_upload_task(task: "UploadTask"):
        pass


class UploadTag(BaseWithUtils):
    __tablename__ = "upload_tags"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    upload_task_id = Column(Integer)
    name = Column(String, default=None)


UploadTask.model = UploadTask
