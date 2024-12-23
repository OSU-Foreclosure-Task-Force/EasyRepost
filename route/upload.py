from API.upload import get_upload_api, UploadAPI
from fastapi import APIRouter
from models.TaskModels import (TaskFilter, UploadTask, NewUploadTask, EditDownloadTask,
                               PersistedUploadTaskResponse, PersistedUploadTaskListResponse)
from model import BaseResponse


class UploadRoute:
    def __init__(self, upload_api: UploadAPI = get_upload_api()):
        self._api = upload_api

    def register_to_router(self, router: APIRouter):
        router.add_api_route("/get_all", self.get_all_upload_tasks, methods=["POST"])
        router.add_api_route("/", self.add_new_upload_task, methods=["POST"])
        router.add_api_route("/sync/", self.add_new_upload_task_sync, methods=["POST"])
        router.add_api_route("/sync/{id}", self.edit_upload_task_sync, methods=["POST"])
        router.add_api_route("/{id}", self.get_upload_task, methods=["GET"])
        router.add_api_route("/{id}", self.edit_upload_task, methods=["POST"])
        router.add_api_route("/{id}", self.pause_upload_task, methods=["PUT"])
        router.add_api_route("/{id}", self.cancel_upload_task, methods=["DELETE"])
        router.add_api_route("/{id}/force", self.force_upload, methods=["GET"])

    async def get_all_upload_tasks(self, task_filter: TaskFilter) -> PersistedUploadTaskListResponse:
        """Retrieve all upload tasks"""

        tasks = await self._api.get_all_upload_tasks(task_filter.states, task_filter.filter_out)
        return PersistedUploadTaskListResponse(payloads=[task.pydantic for task in tasks])

    async def get_upload_task(self, id: int) -> PersistedUploadTaskResponse:
        """Retrieve an upload task by its ID"""
        task = await self._api.get_upload_task(id)
        return PersistedUploadTaskResponse(payload=task.pydantic)

    async def add_new_upload_task(self, task: NewUploadTask) -> BaseResponse:
        """Add a new upload task"""
        new_task = UploadTask(**task.model_dump())
        success = await self._api.add_new_upload_task(new_task)
        return BaseResponse(
            success=success,
            message="task added successfully" if success else "failed to add a new task"
        )

    async def add_new_upload_task_sync(self, task: NewUploadTask) -> PersistedUploadTaskResponse:
        """Add a new upload task and return the persisted task"""
        new_task = UploadTask(**task.model_dump())
        persisted_task = await self._api.add_new_upload_task_sync(new_task)
        return PersistedUploadTaskResponse(payload=persisted_task.pydantic)

    async def edit_upload_task(self, id: int, task: EditDownloadTask) -> BaseResponse:
        """Edit an existing upload task"""
        new_task = UploadTask(id=id, **task.model_dump(exclude_none=True))
        success = await self._api.edit_upload_task(new_task)
        return BaseResponse(
            success=success,
            message="task edited successfully" if success else "failed to edit a new task"
        )

    async def edit_upload_task_sync(self, id: int, task: EditDownloadTask) -> PersistedUploadTaskResponse:
        """Edit an existing upload task and return the persisted task"""
        new_task = UploadTask(id=id, **task.model_dump(exclude_none=True))
        persisted_task = await self._api.edit_upload_task_sync(new_task)
        return PersistedUploadTaskResponse(payload=persisted_task.pydantic)

    async def pause_upload_task(self, id: int) -> BaseResponse:
        """Pause an upload task by its ID"""
        success = await self._api.pause_upload_task(id)
        return BaseResponse(
            success=success,
            message="paused successfully" if success else "failed to emit a pause event"
        )

    async def cancel_upload_task(self, id: int) -> BaseResponse:
        """Cancel an upload task by its ID"""
        success = await self._api.cancel_upload_task(id)
        return BaseResponse(
            success=success,
            message="cancelled successfully" if success else "failed to emit a cancel event"
        )

    async def force_upload(self, id: int) -> BaseResponse:
        """Force an upload task by its ID"""
        success = await self._api.force_upload(id)
        return BaseResponse(
            success=success,
            message="forced successfully" if success else "failed to emit a force event"
        )


upload_router = APIRouter(prefix="/upload")
upload_route = UploadRoute()
upload_route.register_to_router(upload_router)
