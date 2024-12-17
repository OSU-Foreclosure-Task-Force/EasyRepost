import asyncio
from typing import Any

from pydantic import BaseModel, Field
from event.Event import Event
from model import DownloadTask, Subscription, UploadTask, Task


class Feed(BaseModel):
    url: str = Field(...)


class ChannelUpdate(Event):
    def emit(self, feed: Feed) -> bool:
        return super().emit(feed)


class MessageEvent(Event):
    def emit(self, message: str) -> bool:
        return super().emit(message)


class SubscriptionEvent(Event):
    def emit(self, subscription: Subscription) -> bool:
        return super().emit(subscription)


class LoadEvent(Event):
    def emit(self, task: Task) -> bool:
        return super().emit(task)


class DownloadEvent(Event):
    def emit(self, download_task: DownloadTask) -> bool:
        return super().emit(download_task)


class UploadEvent(Event):
    def emit(self, upload_task: UploadTask) -> bool:
        return super().emit(upload_task)


class ExceptionEvent(Event):
    def emit(self, exception: Exception) -> bool:
        return super().emit(exception)