from handler.UploaderSessions.bilibili import BilibiliSession
from handler.Uploader import Uploader
from models.TaskModels import UploadTask
from typing import Callable

channel = BilibiliSession(uid=0,
                          type=0,
                          cookie="example_cookie")
uploaders: dict[str, Callable[..., Uploader] | type[Uploader]] = {
    'example_session_name': channel.get_uploader
}


def get_uploader(task: UploadTask):
    return uploaders[task.site](task)
