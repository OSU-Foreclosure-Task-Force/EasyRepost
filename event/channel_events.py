from typing import Any, Coroutine, Callable
from pydantic import BaseModel

from Event import Event


class UpdateInfo(BaseModel):
    pass


class ChannelUpdate(Event):
    def emit(self, update_info: UpdateInfo) -> Coroutine[Any, Any, list[tuple[Callable[[...], Any], Any]]]:
        return super().emit(update_info)
