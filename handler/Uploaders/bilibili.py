import asyncio
from event import upload_notification
from handler.Uploader import Uploader
from Dependency.bilibili_uploader import BilibiliUploader as BiliUploader
from models.TaskModels import UploadTask
from multiprocessing import Process, Pipe


class BilibiliUploader(Uploader):
    def __init__(self,
                 task: UploadTask,
                 uid: int,
                 type: int,
                 cookie: str,
                 max_retry: int,
                 max_workers: int,
                 chunk_size: int,
                 profile: str,
                 cdn: str):
        super().__init__(task)
        self._receiver, self._sender = Pipe(False)
        self._bili_uploader: BiliUploader = BiliUploader(
            uid=uid,
            type=type,
            cookie=cookie,
            max_retry=max_retry,
            max_workers=max_workers,
            chunk_size=chunk_size,
            profile=profile,
            cdn=cdn,
            notification_event=upload_notification,
            pipe=self._sender
        )
        self.process: Process | None = None

    async def catch_throw_exception(self):
        try:
            exception = await asyncio.to_thread(self._receiver.recv)
            raise exception
        except asyncio.CancelledError:
            return

    async def start(self):
        self.process = Process(target=self._bili_uploader.upload, kwargs={
            "filepath": str(self.task.file_path),
            "title": self.task.name,
            "tid": self.task.tid
        })
        self.process.start()
        catcher = asyncio.create_task(self.catch_throw_exception())
        await asyncio.to_thread(self.process.join)
        catcher.cancel()

    async def cancel(self):
        self.process.terminate()
