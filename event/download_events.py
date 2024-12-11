from pydantic import BaseModel

from Event import Event


class DownloadTask(BaseModel):
    pass


class DownloadEvent(Event):
    def emit(self, download_task: DownloadTask) -> bool:
        return super().emit(download_task)


