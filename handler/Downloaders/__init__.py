from handler.Downloaders.YTDLPDownloader import YTDLPDownloader
from models.TaskModels import DownloadTask
from pathlib import Path
from config import CACHE_PATH, CACHE_MAX_SIZE, CACHE_CHECK_SIZE_INTERVAL
from handler.Downloader import Downloader
from typing import Callable

downloaders: dict[str, Callable[..., Downloader] | type[Downloader]] = {
    'youtube': YTDLPDownloader
}


def get_downloader(task: DownloadTask,
                   cache_path: Path = CACHE_PATH,
                   cache_max_size: int = CACHE_MAX_SIZE,
                   cache_check_size_interval: float = CACHE_CHECK_SIZE_INTERVAL) -> Downloader:
    return downloaders[task.site](cache_path, cache_max_size, cache_check_size_interval)
