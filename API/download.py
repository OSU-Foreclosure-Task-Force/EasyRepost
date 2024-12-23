from models.TaskModels import TaskState, DownloadTask
from event import download_pause, download_cancel, force_download, new_download, edit_download
from typing import Callable, Awaitable
from handler.Scheduler import get_download_scheduler
import config


class DownloadAPI:
    def __init__(self,
                 add_new_task: Callable[[DownloadTask], bool],
                 add_new_task_sync: Callable[[DownloadTask], Awaitable[DownloadTask]],
                 edit_task: Callable[[DownloadTask], bool],
                 edit_task_sync: Callable[[DownloadTask], Awaitable[DownloadTask]],
                 get_all_tasks: Callable[[frozenset[TaskState], bool], Awaitable[list[DownloadTask]]],
                 get_task: Callable[[int], Awaitable[DownloadTask]],
                 pause_task: Callable[[DownloadTask], bool],
                 cancel_task: Callable[[DownloadTask], bool],
                 force_task: Callable[[DownloadTask], bool]
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

    async def get_all_download_tasks(self, task_state_filter: frozenset[TaskState] = frozenset(),
                                     filter_out: bool = False) -> list[DownloadTask]:
        return await self._get_all_tasks(task_state_filter, filter_out)

    async def get_download_task(self, id: int) -> DownloadTask:
        return await self._get_task(id)

    async def add_new_download_task(self, task: DownloadTask) -> bool:
        return self._add_new_task(task)

    async def add_new_download_task_sync(self, task: DownloadTask) -> DownloadTask:
        return await self._add_new_task_sync(task)

    async def edit_download_task(self, task: DownloadTask) -> bool:
        return self._edit_task(task)

    async def edit_download_task_sync(self, task: DownloadTask) -> DownloadTask:
        return await self._edit_task_sync(task)

    async def pause_download_task(self, id: int) -> bool:
        task = await self._get_task(id)
        return self._pause_task(task)

    async def cancel_download_task(self, id: int) -> bool:
        task = await self._get_task(id)
        return self._cancel_task(task)

    async def force_download(self, id: int) -> bool:
        task = await self._get_task(id)
        return self._force_task(task)


def get_download_api() -> DownloadAPI:
    return DownloadAPI(
        add_new_task=new_download.emit,
        add_new_task_sync=get_download_scheduler().add_new_task,
        edit_task=edit_download.emit,
        edit_task_sync=get_download_scheduler().edit_task,
        get_all_tasks=DownloadTask.get_tasks_by_state,
        get_task=DownloadTask.get,
        pause_task=download_pause.emit,
        cancel_task=download_cancel.emit,
        force_task=force_download.emit
    )
