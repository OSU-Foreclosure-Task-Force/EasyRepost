from pydantic import BaseModel, Field
from event.Event import Event


class Feed(BaseModel):
    url: str = Field(...)


class ChannelUpdate(Event):
    def emit(self, feed: Feed) -> bool:
        return super().emit(feed)
