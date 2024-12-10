from typing import Any, Coroutine, Callable
from pydantic import BaseModel

from Event import Event


class DownloadTask(BaseModel):
    pass


class DownloadEvent(Event):
    def emit(self, download_task: DownloadTask) -> Coroutine[Any, Any, list[tuple[Callable[[...], Any], Any]]]:
        return super().emit(download_task)


class NewDownload(DownloadEvent):
    pass


class DownloadPause(DownloadEvent):
    pass


class DownloadContinue(DownloadEvent):
    pass


class DownloadCancel(DownloadEvent):
    pass
