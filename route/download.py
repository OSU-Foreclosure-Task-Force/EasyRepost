from API.download import get_download_api, DownloadAPI
from fastapi import Depends, APIRouter
from pydantic import BaseModel


class DownloadTask(BaseModel):
    pass


class DownloadRoute:
    def __init__(self, download_api: DownloadAPI = Depends(get_download_api)):
        self._api = download_api

    def register_to_router(self, router: APIRouter):
        router.add_api_route("/", self.get_all_download_tasks, methods=["GET"])
        router.add_api_route("/", self.add_new_download_task, methods=["POST"])
        router.add_api_route("/{id}", self.get_download_task, methods=["GET"])
        router.add_api_route("/{id}", self.edit_download_task, methods=["POST"])
        router.add_api_route("/{id}", self.pause_download_task, methods=["PUT"])
        router.add_api_route("/{id}", self.cancel_download_task, methods=["DELETE"])
        router.add_api_route("/{id}/force", self.force_download, methods=["GET"])

    async def get_all_download_tasks(self):
        """Retrieve all download tasks"""
        return await self._api.get_all_download_tasks()

    async def get_download_task(self, id: int):
        """Retrieve a download task by its ID"""
        return await self._api.get_download_task(id)

    async def add_new_download_task(self, task: DownloadTask):
        """Add a new download task"""
        return await self._api.add_new_download_task(task)

    async def edit_download_task(self, id: int, task: DownloadTask):
        """Edit an existing download task by its ID"""
        return await self._api.edit_download_task(id, task)

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
