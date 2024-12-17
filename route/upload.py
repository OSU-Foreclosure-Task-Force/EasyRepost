from API.upload import get_upload_api, UploadAPI
from fastapi import Depends, APIRouter
from model import NewTask, UploadTask, TaskFilter


class NewUploadTask(NewTask):
    destination: str


class PersistedUploadTask(NewUploadTask):
    id: int


class UploadRoute:
    def __init__(self, upload_api: UploadAPI = Depends(get_upload_api)):
        self._api = upload_api

    def register_to_router(self, router: APIRouter):
        router.add_api_route("/", self.get_all_upload_tasks, methods=["GET"])
        router.add_api_route("/", self.add_new_upload_task, methods=["POST"])
        router.add_api_route("/{id}", self.get_upload_task, methods=["GET"])
        router.add_api_route("/{id}", self.edit_upload_task, methods=["POST"])
        router.add_api_route("/{id}", self.pause_upload_task, methods=["PUT"])
        router.add_api_route("/{id}", self.cancel_upload_task, methods=["DELETE"])
        router.add_api_route("/{id}/force", self.force_upload, methods=["GET"])

    async def get_all_upload_tasks(self, task_filter: TaskFilter) -> dict[str, list[PersistedUploadTask]]:
        """Retrieve all upload tasks"""
        return {"tasks": await self._api.get_all_upload_tasks(task_filter.states, task_filter.filter_out)}

    async def get_upload_task(self, id: int):
        """Retrieve an upload task by its ID"""
        return await self._api.get_upload_task(id)

    async def add_new_upload_task(self, task: NewUploadTask):
        """Add a new upload task"""
        UploadTask(**task.model_dump())
        return await self._api.add_new_upload_task(task)

    async def edit_upload_task(self, task: PersistedUploadTask):
        """Edit an existing upload task by its ID"""
        UploadTask(**task.model_dump())
        return await self._api.edit_upload_task(task)

    async def pause_upload_task(self, id: int):
        """Pause an upload task by its ID"""
        return await self._api.pause_upload_task(id)

    async def cancel_upload_task(self, id: int):
        """Cancel an upload task by its ID"""
        return await self._api.cancel_upload_task(id)

    async def force_upload(self, id: int):
        """Force an upload task by its ID"""
        return await self._api.force_upload(id)


upload_router = APIRouter(prefix="/upload")
upload_route = UploadRoute()
upload_route.register_to_router(upload_router)
