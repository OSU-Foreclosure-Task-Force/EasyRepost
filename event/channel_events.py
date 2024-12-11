from pydantic import BaseModel

from Event import Event


class UpdateInfo(BaseModel):
    pass


class ChannelUpdate(Event):
    def emit(self, update_info: UpdateInfo) -> bool:
        return super().emit(update_info)
