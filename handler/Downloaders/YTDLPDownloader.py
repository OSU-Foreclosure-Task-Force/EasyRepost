import asyncio.subprocess
from pathlib import Path
from handler.Downloader import Downloader
from models.TaskModels import DownloadTask
from asyncio.subprocess import create_subprocess_shell, PIPE, Process


class YTDLPDownloader(Downloader):

    def __init__(self, task: DownloadTask, cache_path: Path, cache_max_size: int, cache_check_size_interval: float,
                 process: Process | None = None):
        super().__init__(task, cache_path, cache_max_size, cache_check_size_interval)
        self._process: Process | None = process
        self._progress: float = 0

    def _load_args(self) -> str:
        thumbnail_arg = "--write-thumbnail" if self.task.with_thumbnail else ""
        description_arg = "--write-description" if self.task.with_description else ""
        return (f'yt-dlp '
                f'{thumbnail_arg} '
                f'{description_arg} '
                f'--rm-cache-dir '
                f'-o {self.CACHE_PATH.joinpath(self.task.name)}.mp4 '
                f'-f bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio '
                f'{self.task.url}')

    @staticmethod
    def _read_progress(line: str) -> float:
        pass

    async def _update_progress(self, process: Process):
        async for line in process.stdout:
            self._progress = self._read_progress(line)

    @property
    def progress(self):
        return self._progress

    def _start_update_progress(self, process: Process):
        asyncio.create_task(self._update_progress(process))

    async def start(self):
        await self.wait_for_enough_space()
        command = self._load_args()
        self._process = await create_subprocess_shell(command, stdout=PIPE, stderr=PIPE)
        self._start_update_progress(self._process)
        stdout, stderr = await self._process.communicate()
        print(stdout)
        print(stderr)

    async def cancel(self):
        self._process.terminate()
