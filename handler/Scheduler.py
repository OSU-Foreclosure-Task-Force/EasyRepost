from logging import getLogger

logger = getLogger(__name__)
from handler.BaseScheduler import BaseScheduler
from event import download_suspend, download_pause, download_resume, download_cancel, \
    force_download, downloading, download_complete, download_retry, download_waiting, new_download, edit_download
from event import upload_suspend, upload_pause, upload_resume, upload_cancel, force_upload, uploading, \
    upload_complete, upload_retry, upload_waiting, new_upload, edit_upload
from config import DOWNLOAD_RETRY_DELAY, DOWNLOAD_MAX_CONCURRENT, UPLOAD_RETRY_DELAY, UPLOAD_MAX_CONCURRENT
from handler.Downloaders import get_downloader
from handler.Uploaders import get_uploader
from model import DownloadTask, UploadTask, Task

__all__ = ["get_download_scheduler", "get_upload_scheduler", "Scheduler"]


class Scheduler:

    def __init__(self, name: str, base_scheduler: BaseScheduler):
        self._name: str = name
        self._base_scheduler = base_scheduler

    async def run(self):
        await self._base_scheduler.run()

    async def load_tasks(self):
        await self._base_scheduler.load_tasks()

    async def add_new_task(self, new_task: Task):
        await self._base_scheduler.add_new_task(new_task)

    async def edit_task(self, task: Task):
        try:
            await self._base_scheduler.edit_task(task)
        except RuntimeError as e:
            logger.warning(e)


_download_scheduler: Scheduler | None = None
_upload_scheduler: Scheduler | None = None


def get_download_scheduler() -> Scheduler:
    global _download_scheduler
    if _download_scheduler is None:
        _download_scheduler = Scheduler("download scheduler", BaseScheduler(
            task_type=DownloadTask,
            get_all_tasks_from_db=DownloadTask.get_multiple,
            add_task_to_db=lambda task: DownloadTask.create(**task.to_dict()),
            update_db_task=lambda task: DownloadTask.update(**task.to_dict()),
            destroy_task=DownloadTask.destroy_download_task,
            retry_delay=DOWNLOAD_RETRY_DELAY,
            max_concurrent=DOWNLOAD_MAX_CONCURRENT,
            worker_factory=get_downloader,
            suspend_event=download_suspend,
            pause_event=download_pause,
            resume_event=download_resume,
            cancel_event=download_cancel,
            force_start_event=force_download,
            retry_event=download_retry,
            new_task_event=new_download,
            edit_task_event=edit_download,
            wait_event=download_waiting,
            processing_event=downloading,
            complete_event=download_complete,
        ))
    return _download_scheduler



def get_upload_scheduler() -> Scheduler:
    global _upload_scheduler
    if _upload_scheduler is None:
        _upload_scheduler = Scheduler("upload scheduler", BaseScheduler(
            task_type=UploadTask,
            get_all_tasks_from_db=UploadTask.get_multiple,
            add_task_to_db=lambda task: UploadTask.create(**task.to_dict()),
            update_db_task=lambda task: UploadTask.update(**task.to_dict()),
            destroy_task=UploadTask.destroy_upload_task,
            retry_delay=UPLOAD_RETRY_DELAY,
            max_concurrent=UPLOAD_MAX_CONCURRENT,
            worker_factory=get_uploader,
            suspend_event=upload_suspend,
            pause_event=upload_pause,
            resume_event=upload_resume,
            cancel_event=upload_cancel,
            force_start_event=force_upload,
            retry_event=upload_retry,
            new_task_event=new_upload,
            edit_task_event=edit_upload,
            wait_event=upload_waiting,
            processing_event=uploading,
            complete_event=upload_complete,
        ))
    return _upload_scheduler