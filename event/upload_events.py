from model import UploadTask
from event.Event import Event


class UploadEvent(Event):
    def emit(self, upload_task: UploadTask) -> bool:
        return super().emit(upload_task)
