import asyncio
from pathlib import Path
from handler.BaseLoader import BaseLoader
from models.TaskModels import DownloadTask
import os


class Downloader(BaseLoader):
    def __init__(self, task:DownloadTask, cache_path: Path, cache_max_size: int, cache_check_size_interval: float):
        super().__init__(task)
        self.task: DownloadTask = self.task
        self.CACHE_PATH: Path = cache_path
        self.cache_space: int = cache_max_size
        self.CACHE_CHECK_SIZE_INTERVAL = cache_check_size_interval

    def get_task_size(self):
        raise NotImplementedError

    def load_task(self, task: DownloadTask):
        self.task = task

    async def wait_for_enough_space(self):
        try:
            task_size = self.get_task_size()
        except NotImplementedError:
            return
        while True:
            size = 0
            for root, dirs, files in os.walk(self.CACHE_PATH):
                size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
            if self.cache_space - task_size >= 0:
                break
            await asyncio.sleep(self.CACHE_CHECK_SIZE_INTERVAL)
