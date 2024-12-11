from event.download_events import DownloadTask
from model import DownloadTask
from event import download_pause, download_cancel, force_download


class DownloadAPI:
    @staticmethod
    async def get_all_download_tasks() -> list[DownloadTask]:
        return await DownloadTask.get_multiple()

    @staticmethod
    async def get_download_task(id: int) -> DownloadTask:
        return await DownloadTask.get(id)

    @staticmethod
    async def add_new_download_task(task: DownloadTask) -> DownloadTask:
        return await DownloadTask.create(**task.to_dict())

    @staticmethod
    async def edit_download_task(id: int, task: DownloadTask) -> DownloadTask:
        return await DownloadTask.update(id, **task.to_dict())

    @staticmethod
    async def pause_download_task(id: int) -> bool:
        task = await DownloadTask.get(id)
        download_pause.emit(task)
        return True

    @staticmethod
    async def cancel_download_task(id: int) -> bool:
        task = await DownloadTask.get(id)
        download_cancel.emit(task)
        return True

    @staticmethod
    async def force_download(id: int) -> bool:
        task = await DownloadTask.get(id)
        force_download(task)
        return True


def get_download_api() -> DownloadAPI:
    return DownloadAPI()
