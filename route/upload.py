from API.upload import get_upload_api, UploadAPI
from fastapi import Depends, APIRouter
from event.upload_events import UploadTask


class UploadRoute:
    def __init__(self, upload_api: UploadAPI = Depends(get_upload_api)):
        self.__api = upload_api

    def register_to_router(self, router: APIRouter):
        router.add_api_route("/", self.get_all_upload_tasks, methods=["GET"])
        router.add_api_route("/", self.add_new_upload_task, methods=["POST"])
        router.add_api_route("/{id}", self.get_upload_task, methods=["GET"])
        router.add_api_route("/{id}", self.edit_upload_task, methods=["POST"])
        router.add_api_route("/{id}", self.pause_upload_task, methods=["PUT"])
        router.add_api_route("/{id}", self.cancel_upload_task, methods=["DELETE"])
        router.add_api_route("/{id}/force", self.force_upload, methods=["GET"])

    async def get_all_upload_tasks(self):
        """Retrieve all upload tasks"""
        return await self.__api.get_all_upload_tasks()

    async def get_upload_task(self, id: int):
        """Retrieve an upload task by its ID"""
        return await self.__api.get_upload_task(id)

    async def add_new_upload_task(self, task: UploadTask):
        """Add a new upload task"""
        return await self.__api.add_new_upload_task(task)

    async def edit_upload_task(self, id: int, task: UploadTask):
        """Edit an existing upload task by its ID"""
        return await self.__api.edit_upload_task(id, task)

    async def pause_upload_task(self, id: int):
        """Pause an upload task by its ID"""
        return await self.__api.pause_upload_task(id)

    async def cancel_upload_task(self, id: int):
        """Cancel an upload task by its ID"""
        return await self.__api.cancel_upload_task(id)

    async def force_upload(self, id: int):
        """Force an upload task by its ID"""
        return await self.__api.force_upload(id)


upload_router = APIRouter(prefix="/upload")
upload_route = UploadRoute()
upload_route.register_to_router(upload_router)
