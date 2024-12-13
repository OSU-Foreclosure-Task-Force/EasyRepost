from BaseLoader import BaseLoader
from model import DownloadTask


class Downloader(BaseLoader):
    pass


def get_downloader(task: DownloadTask) -> Downloader:
    return Downloader(task)
