from BaseScheduler import BaseScheduler

from event import download_suspend, channel_update, download_pause, download_resume, download_cancel, \
    force_download, downloading, download_complete, download_retry, download_waiting, new_download
from config import DOWNLOAD_RETRY_DELAY, DOWNLOAD_MAX_CONCURRENT, UPLOAD_RETRY_DELAY, UPLOAD_MAX_CONCURRENT
from Downloader import Downloader, get_downloader
from Uploader import Uploader, get_uploader
from model import DownloadTask, UploadTask


class Scheduler:
    def __init__(self, base_scheduler: BaseScheduler):
        self._base_scheduler = base_scheduler

    async def run(self):
        await self._base_scheduler.run()

    async def add_new_task(self, url: str):
        await self._base_scheduler.add_new_task(url)


async def destroy_download_task(task: DownloadTask):
    pass


download_scheduler = Scheduler(BaseScheduler(
    name="download scheduler",
    task_type=DownloadTask,
    get_all_tasks_from_db=DownloadTask.get_multiple,
    add_task_to_db=lambda task: DownloadTask.create(**task.to_dict()),
    update_db_task=lambda task: DownloadTask.update(**task.to_dict()),
    destroy_task=destroy_download_task,
    retry_delay=DOWNLOAD_RETRY_DELAY,
    max_concurrent=DOWNLOAD_MAX_CONCURRENT,
    worker_factory=get_downloader,
    suspend_event=download_suspend,
    feed_event=channel_update,
    pause_event=download_pause,
    resume_event=download_resume,
    cancel_event=download_cancel,
    force_start_event=force_download,
    retry_event=download_retry,
    new_task_event=new_download,
    wait_event=download_waiting,
    processing_event=downloading,
    complete_event=download_complete,
))
