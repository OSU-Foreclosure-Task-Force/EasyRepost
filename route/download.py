from API.download import get_download_api, DownloadAPI
from fastapi import APIRouter
from pydantic import BaseModel, Field
from model import TaskPriority, DownloadTask, TaskFilter, NewTask


class NewDownloadTask(NewTask):
    name: str
    url: str
    site: str
    wait_time: int = Field(0)
    priority: int = Field(TaskPriority.DEFAULT)
    with_description: bool = Field(True)
    with_subtitles: bool = Field(False)
    with_thumbnail: bool = Field(True)
    format: str = Field("")
    resolution_x: int = Field(0)
    resolution_y: int = Field(0)
    video_codec: str = Field("")
    audio_codec: str = Field("")
    video_bit_rate: int = Field(0)
    audio_bit_rate: int = Field(0)
    sample_rate: int = Field(0)
    frame_rate: int = Field(0)


class PersistedDownloadTask(NewDownloadTask):
    id: int


class DownloadRoute:
    def __init__(self, download_api: DownloadAPI = get_download_api()):
        self._api = download_api

    def register_to_router(self, router: APIRouter):
        router.add_api_route("/get_all", self.get_all_download_tasks, methods=["POST"])
        router.add_api_route("/", self.add_new_download_task, methods=["POST"])
        router.add_api_route("/{id}", self.get_download_task, methods=["GET"])
        router.add_api_route("/{id}", self.edit_download_task, methods=["POST"])
        router.add_api_route("/{id}", self.pause_download_task, methods=["PUT"])
        router.add_api_route("/{id}", self.cancel_download_task, methods=["DELETE"])
        router.add_api_route("/{id}/force", self.force_download, methods=["GET"])

    async def get_all_download_tasks(self, task_filter: TaskFilter) -> dict[str, list[PersistedDownloadTask]]:
        """Retrieve all download tasks"""
        return {"tasks": await self._api.get_all_download_tasks(task_filter.states, task_filter.filter_out)}

    async def get_download_task(self, id: int):
        """Retrieve a download task by its ID"""
        return await self._api.get_download_task(id)

    async def add_new_download_task(self, task: NewDownloadTask):
        """Add a new download task"""
        new_task = DownloadTask(**task.model_dump())
        return await self._api.add_new_download_task(new_task)

    async def edit_download_task(self, task: PersistedDownloadTask):
        """Edit an existing download task by its ID"""
        new_task = DownloadTask(**task.model_dump())
        return await self._api.edit_download_task(new_task)

    async def pause_download_task(self, id: int):
        """Pause a download task by its ID"""
        return await self._api.pause_download_task(id)

    async def cancel_download_task(self, id: int):
        """Cancel a download task by its ID"""
        return await self._api.cancel_download_task(id)

    async def force_download(self, id: int):
        """Force a download task by its ID"""
        return await self._api.force_download(id)


download_router = APIRouter(prefix="/download")
download_route = DownloadRoute()
download_route.register_to_router(download_router)
