from pydantic import BaseModel

from Event import Event


class UploadTask(BaseModel):
    pass


class UploadEvent(Event):
    def emit(self, upload_task: UploadTask) -> bool:
        return super().emit(upload_task)



