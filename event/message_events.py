from event.Event import Event
from pydantic import BaseModel


class Message(BaseModel):
    pass


class MessageEvent(Event):
    def emit(self, message: Message) -> bool:
        return super().emit(message)


