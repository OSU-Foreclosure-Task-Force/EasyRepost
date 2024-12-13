from model import UploadTask
from event import new_upload, upload_pause, upload_cancel, force_upload


class UploadAPI:
    @staticmethod
    async def get_all_upload_tasks() -> list[UploadTask]:
        return await UploadTask.get_multiple()

    @staticmethod
    async def get_upload_task(id: int) -> UploadTask:
        return await UploadTask.get(id)

    @staticmethod
    async def add_new_upload_task(task: UploadTask) -> bool:
        return new_upload.emit(task)

    @staticmethod
    async def edit_upload_task(id: int, task: UploadTask) -> UploadTask:
        return await UploadTask.update(id, **task.to_dict())

    @staticmethod
    async def pause_upload_task(id: int) -> bool:
        task = await UploadTask.get(id)
        return upload_pause.emit(task)

    @staticmethod
    async def cancel_upload_task(id: int) -> bool:
        task = await UploadTask.get(id)
        return upload_cancel.emit(task)

    @staticmethod
    async def force_upload(id: int) -> bool:
        task = await UploadTask.get(id)
        return force_upload.emit(task)


def get_upload_api() -> UploadAPI:
    return UploadAPI()
