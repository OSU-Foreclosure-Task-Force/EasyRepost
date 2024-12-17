from handler.Uploaders.bilibili import BilibiliUploader
from handler.Uploader import UploadTask
from handler.UploaderSession import UploaderSession
from model import UploaderSessionEncrypted
from dataclasses import dataclass


@dataclass
class BilibiliSession(UploaderSession):
    uid: int
    type: int
    cookie: str
    max_retry: int = 5
    max_threads: int = 8
    chunk_size: int = 4 * 1024 * 1024
    profile: str = 'ugcupos/yb'
    cdn: str = 'ws'

    @classmethod
    def decrypt(cls, encrypted_session: UploaderSessionEncrypted, *args, **kwargs):
        pass

    def encrypt(self) -> str:
        pass

    def get_uploader(self, task: UploadTask) -> BilibiliUploader:
        return BilibiliUploader(task=task,
                                uid=self.uid,
                                type=self.type,
                                cookie=self.cookie,
                                max_retry=self.max_retry,
                                max_workers=self.max_threads,
                                chunk_size=self.chunk_size,
                                profile=self.profile,
                                cdn=self.cdn)
