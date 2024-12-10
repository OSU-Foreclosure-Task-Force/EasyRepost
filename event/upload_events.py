from typing import Any, Coroutine, Callable
from pydantic import BaseModel

from Event import Event


class UploadTask(BaseModel):
    pass


class UploadEvent(Event):
    def emit(self, upload_task: UploadTask) -> Coroutine[Any, Any, list[tuple[Callable[[...], Any], Any]]]:
        return super().emit(upload_task)


class NewUpload(UploadEvent):
    pass


class UploadPause(UploadEvent):
    pass


class UploadContinue(UploadEvent):
    pass


class UploadCancel(UploadEvent):
    pass
