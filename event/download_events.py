from model import DownloadTask
from event.Event import Event


class DownloadEvent(Event):
    def emit(self, download_task: DownloadTask) -> bool:
        return super().emit(download_task)
