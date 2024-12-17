from handler.BaseLoader import BaseLoader
from model import UploadTask


class Uploader(BaseLoader):
    def __init__(self, task: UploadTask):
        super().__init__(task)
        self.task: UploadTask = self.task
