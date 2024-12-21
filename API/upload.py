from models.TaskModels import TaskState, UploadTask
from event import upload_pause, upload_cancel, force_upload, new_upload, edit_upload
from handler.Scheduler import get_upload_scheduler
from typing import Callable, Awaitable
from config import ENABLE_AUTO_UPLOAD

class UploadAPI:
    def __init__(self,
                 add_new_task: Callable[[UploadTask],bool],
                 add_new_task_sync: Callable[[UploadTask],Awaitable[UploadTask]],
                 edit_task: Callable[[UploadTask],bool],
                 edit_task_sync: Callable[[UploadTask], Awaitable[UploadTask]],
                 get_all_tasks: Callable[[frozenset[TaskState], bool], Awaitable[list[UploadTask]]],
                 get_task: Callable[[int], Awaitable[UploadTask]],
                 pause_task: Callable[[UploadTask], bool],
                 cancel_task: Callable[[UploadTask], bool],
                 force_task: Callable[[UploadTask], bool]
                 ):
        self._add_new_task = add_new_task
        self._add_new_task_sync = add_new_task_sync
        self._edit_task = edit_task
        self._edit_task_sync = edit_task_sync
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

    async def add_new_upload_task(self, task: UploadTask) -> bool:
        return self._add_new_task(task)

    async def add_new_upload_task_sync(self, task: UploadTask) -> UploadTask:
        return await self._add_new_task_sync(task)

    async def edit_upload_task(self, task: UploadTask) -> bool:
        return self._edit_task(task)

    async def edit_upload_task_sync(self, task: UploadTask) -> UploadTask:
        return await self._edit_task_sync(task)

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
    if not ENABLE_AUTO_UPLOAD:
        raise NotImplementedError("Auto upload is disabled")
    return UploadAPI(
        add_new_task=new_upload.emit,
        add_new_task_sync=get_upload_scheduler().add_new_task,
        edit_task=edit_upload.emit,
        edit_task_sync=get_upload_scheduler().edit_task,
        get_all_tasks=UploadTask.get_tasks_by_state,
        get_task=UploadTask.get,
        pause_task=upload_pause.emit,
        cancel_task=upload_cancel.emit,
        force_task=force_upload.emit
    )
