import enum
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum, select, Boolean
from database import async_session
from model import BaseWithUtils, DataResponse, DataListResponse
from config import AUTO_DOWNLOAD_WAIT_TIME, AUTO_UPLOAD_WAIT_TIME


# pydantic models (can be used for param parsing)

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


class NewTask(BaseModel):
    name: str
    wait_time: int = Field(None)
    priority: int = Field(TaskPriority.DEFAULT)


class PersistedTask(NewTask):
    id: int
    extension: str
    state: TaskState


class NewDownloadTask(NewTask):
    url: str
    site: str
    wait_time: int = Field(AUTO_DOWNLOAD_WAIT_TIME)
    with_description: bool = Field(True)
    with_subtitles: bool = Field(False)
    with_thumbnail: bool = Field(True)
    format: str = Field(None)
    resolution_x: int = Field(None)
    resolution_y: int = Field(None)
    video_codec: str = Field(None)
    audio_codec: str = Field(None)
    video_bit_rate: int = Field(None)
    audio_bit_rate: int = Field(None)
    sample_rate: int = Field(None)
    frame_rate: int = Field(None)


class PersistedDownloadTask(PersistedTask, NewDownloadTask):
    id: int


class PersistedDownloadTaskResponse(DataResponse):
    payload: PersistedDownloadTask


class PersistedDownloadTaskListResponse(DataListResponse):
    payloads: list[PersistedDownloadTaskResponse]


class EditDownloadTask(PersistedDownloadTask):
    name: str = Field(None)
    url: str = Field(None)
    site: str = Field(None)
    wait_time: int = Field(None)
    priority: int = Field(None)
    with_description: bool = Field(None)
    with_subtitles: bool = Field(None)
    with_thumbnail: bool = Field(None)
    format: str = Field(None)
    resolution_x: int = Field(None)
    resolution_y: int = Field(None)
    video_codec: str = Field(None)
    audio_codec: str = Field(None)
    video_bit_rate: int = Field(None)
    audio_bit_rate: int = Field(None)
    sample_rate: int = Field(None)
    frame_rate: int = Field(None)


class NewUploadTask(NewTask):
    wait_time: int = Field(AUTO_UPLOAD_WAIT_TIME)
    destination: str


class PersistedUploadTask(PersistedTask, NewUploadTask):
    id: int


class PersistedUploadTaskResponse(DataResponse):
    payload: PersistedUploadTask


class PersistedUploadTaskListResponse(DataListResponse):
    payloads: list[PersistedUploadTask]


class EditUploadTask(PersistedUploadTask):
    name: str = Field(None)
    url: str = Field(None)
    wait_time: int = Field(None)
    priority: int = Field(None)
    destination: str = Field(None)


# SQL ORM Models

class Task(BaseWithUtils):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, default=None)
    extension = Column(String, default=None)
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

    @property
    def pydantic(self) -> PersistedTask:
        return PersistedTask(**self.to_dict())


class DownloadTask(Task):
    __tablename__ = "download_tasks"
    url = Column(String, default=None)
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

    @property
    def pydantic(self) -> PersistedDownloadTask:
        return PersistedDownloadTask(**self.to_dict())


class UploadTask(Task):
    __tablename__ = "upload_tasks"
    destination = Column(String, default=None)

    @staticmethod
    async def destroy_upload_task(task: "UploadTask"):
        pass

    @property
    def pydantic(self) -> PersistedUploadTask:
        return PersistedUploadTask(**self.to_dict())


class UploadTag(BaseWithUtils):
    __tablename__ = "upload_tags"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    upload_task_id = Column(Integer)
    name = Column(String, default=None)
