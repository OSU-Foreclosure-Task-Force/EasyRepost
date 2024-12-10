from typing import Any, Coroutine, Callable

from Event import Event
from pydantic import BaseModel


class Message(BaseModel):
    pass


class MessageEvent(Event):
    def emit(self, message: Message) -> Coroutine[Any, Any, list[tuple[Callable[[...], Any], Any]]]:
        return super().emit(message)


class DownloadFull(MessageEvent):
    pass


class UploadFull(MessageEvent):
    pass


class SendMail(MessageEvent):
    pass


class SendShortMSG(MessageEvent):
    pass


class SendDiscord(MessageEvent):
    pass


class SendQQ(MessageEvent):
    pass
