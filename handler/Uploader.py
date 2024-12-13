from BaseLoader import BaseLoader
from model import UploadTask


class Uploader(BaseLoader):
    pass


def get_uploader(task: UploadTask) -> Uploader:
    return Uploader(task)
