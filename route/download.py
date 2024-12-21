from API.download import get_download_api, DownloadAPI
from fastapi import APIRouter
from models.TaskModels import (TaskFilter, DownloadTask, NewDownloadTask, EditDownloadTask,
                               PersistedDownloadTaskResponse, PersistedDownloadTaskListResponse)
from utils.pydantic import eliminate_missing_values
from model import BaseResponse


class DownloadRoute:
    def __init__(self, download_api: DownloadAPI = get_download_api()):
        self._api = download_api

    def register_to_router(self, router: APIRouter):
        router.add_api_route("/get_all", self.get_all_download_tasks, methods=["POST"])
        router.add_api_route("/", self.add_new_download_task, methods=["POST"])
        router.add_api_route("/sync/", self.add_new_download_task_sync, methods=["POST"])
        router.add_api_route("/sync/{id}", self.edit_download_task_sync, methods=["POST"])
        router.add_api_route("/{id}", self.get_download_task, methods=["GET"])
        router.add_api_route("/{id}", self.edit_download_task, methods=["POST"])
        router.add_api_route("/{id}", self.pause_download_task, methods=["PUT"])
        router.add_api_route("/{id}", self.cancel_download_task, methods=["DELETE"])
        router.add_api_route("/{id}/force", self.force_download, methods=["GET"])

    async def get_all_download_tasks(self, task_filter: TaskFilter) -> PersistedDownloadTaskListResponse:
        """Retrieve all download tasks"""

        tasks = await self._api.get_all_download_tasks(task_filter.states, task_filter.filter_out)
        return PersistedDownloadTaskListResponse(payloads=[task.pydantic for task in tasks])

    async def get_download_task(self, id: int) -> PersistedDownloadTaskResponse:
        """Retrieve a download task by its ID"""
        task = await self._api.get_download_task(id)
        return PersistedDownloadTaskResponse(payload=task.pydantic)

    async def add_new_download_task(self, task: NewDownloadTask) -> BaseResponse:
        """Add a new download task"""
        new_task = DownloadTask(**task.model_dump())
        success = await self._api.add_new_download_task(new_task)
        return BaseResponse(
            success=success,
            message="task added successfully" if success else "failed to add a new task"
        )

    async def add_new_download_task_sync(self, task: NewDownloadTask) -> PersistedDownloadTaskResponse:
        """Add a new download task and return the persisted task"""
        new_task = DownloadTask(**task.model_dump())
        persisted_task = await self._api.add_new_download_task_sync(new_task)
        return PersistedDownloadTaskResponse(payload=persisted_task.pydantic)

    async def edit_download_task(self, task: EditDownloadTask) -> BaseResponse:
        """Edit an existing download task"""
        new_task = DownloadTask(**eliminate_missing_values(task))
        success = await self._api.edit_download_task(new_task)
        return BaseResponse(
            success=success,
            message="task edited successfully" if success else "failed to edit a new task"
        )

    async def edit_download_task_sync(self, task:EditDownloadTask) -> PersistedDownloadTaskResponse:
        """Edit an existing download task and return the persisted task"""
        new_task = DownloadTask(**eliminate_missing_values(task))
        persisted_task = await self._api.edit_download_task_sync(new_task)
        return PersistedDownloadTaskResponse(payload=persisted_task.pydantic)

    async def pause_download_task(self, id: int) -> BaseResponse:
        """Pause a download task by its ID"""
        success = await self._api.pause_download_task(id)
        return BaseResponse(
            success=success,
            message="paused successfully" if success else "failed to emit a pause event"
        )

    async def cancel_download_task(self, id: int) -> BaseResponse:
        """Cancel a download task by its ID"""
        success = await self._api.cancel_download_task(id)
        return BaseResponse(
            success=success,
            message="cancelled successfully" if success else "failed to emit a cancel event"
        )

    async def force_download(self, id: int) -> BaseResponse:
        """Force a download task by its ID"""
        success = await self._api.force_download(id)
        return BaseResponse(
            success=success,
            message="forced successfully" if success else "failed to emit a force event"
        )


download_router = APIRouter(prefix="/download")
download_route = DownloadRoute()
download_route.register_to_router(download_router)
