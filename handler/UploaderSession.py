from handler.Uploader import Uploader, UploadTask
from model import UploaderSessionEncrypted
from dataclasses import dataclass


@dataclass
class UploaderSession:
    @classmethod
    def decrypt(cls, encrypted_session: UploaderSessionEncrypted, *args, **kwargs):
        raise NotImplemented

    def encrypt(self) -> str:
        raise NotImplemented

    def get_uploader(self, task: UploadTask) -> Uploader:
        raise NotImplemented
