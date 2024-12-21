from .Event import Event
from models.SubscriptionModels import Validation, Subscription, Hub, Feed
from models.TaskModels import Task, DownloadTask, UploadTask, NewDownloadTask, NewUploadTask


class FeedEvent(Event):
    def emit(self, feed: Feed) -> bool:
        return super().emit(feed)


class MessageEvent(Event):
    def emit(self, message: str) -> bool:
        return super().emit(message)


class ValidationEvent(Event):
    def emit(self, validation: Validation) -> bool:
        return super().emit(validation)


class HubEvent(Event):
    def emit(self, hub: Hub) -> bool:
        return super().emit(hub)


class SubscriptionEvent(Event):
    def emit(self, subscription: Subscription) -> bool:
        return super().emit(subscription)


class LoadEvent(Event):
    def emit(self, task: Task) -> bool:
        return super().emit(task)


class NewDownloadEvent(Event):
    def emit(self, new_task: NewDownloadTask) -> bool:
        return super().emit(new_task)


class DownloadEvent(Event):
    def emit(self, download_task: DownloadTask) -> bool:
        return super().emit(download_task)


class NewUploadEvent(Event):
    def emit(self, new_task: NewUploadTask) -> bool:
        return super().emit(new_task)


class UploadEvent(Event):
    def emit(self, upload_task: UploadTask) -> bool:
        return super().emit(upload_task)


class ExceptionEvent(Event):
    def emit(self, exception: Exception) -> bool:
        return super().emit(exception)
