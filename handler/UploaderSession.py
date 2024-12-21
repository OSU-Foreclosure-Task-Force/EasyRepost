from handler.Uploader import Uploader
from models.TaskModels import UploadTask
from models.SessionModels import UploaderSessionEncrypted
from dataclasses import dataclass


@dataclass
class UploaderSession:
    @classmethod
    def decrypt(cls, encrypted_session: UploaderSessionEncrypted, *args, **kwargs):
        raise NotImplementedError

    def encrypt(self) -> str:
        raise NotImplementedError

    def get_uploader(self, task: UploadTask) -> Uploader:
        raise NotImplementedError
