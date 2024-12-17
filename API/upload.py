from model import UploadTask, TaskState
from event import upload_pause, upload_cancel, force_upload
from handler.Scheduler import Scheduler, get_upload_scheduler
from typing import Callable, Awaitable

class UploadAPI:
    def __init__(self,
                 scheduler: Scheduler,
                 get_all_tasks: Callable[[frozenset[TaskState], bool], Awaitable[list[UploadTask]]],
                 get_task: Callable[[int], Awaitable[UploadTask]],
                 pause_task: Callable[[UploadTask], bool],
                 cancel_task: Callable[[UploadTask], bool],
                 force_task: Callable[[UploadTask], bool]
                 ):
        self._scheduler = scheduler
        self._get_all_tasks = get_all_tasks
        self._get_task = get_task
        self._pause_task = pause_task
        self._cancel_task = cancel_task
        self._force_task = force_task

    async def get_all_upload_tasks(self, task_state_filter: frozenset[TaskState] = frozenset(),
                                   filter_out: bool = False) -> list[UploadTask]:
        return await self._get_all_tasks(task_state_filter, filter_out)

    async def get_upload_task(self, id: int) -> UploadTask:
        return await self._get_task(id)

    async def add_new_upload_task(self, task: UploadTask) -> UploadTask:
        return await self._scheduler.add_new_task(task)

    async def edit_upload_task(self, task: UploadTask) -> UploadTask:
        return await self._scheduler.edit_task(task)

    async def pause_upload_task(self, id: int) -> bool:
        task = await self._get_task(id)
        return self._pause_task(task)

    async def cancel_upload_task(self, id: int) -> bool:
        task = await self._get_task(id)
        return self._cancel_task(task)

    async def force_upload(self, id: int) -> bool:
        task = await self._get_task(id)
        return self._force_task(task)


def get_upload_api() -> UploadAPI:
    return UploadAPI(
        get_upload_scheduler(),
        UploadTask.get_tasks_by_state,
        UploadTask.get,
        upload_pause.emit,
        upload_cancel.emit,
        force_upload.emit
    )
