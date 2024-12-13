from pydantic import BaseModel, Field


class Validation(BaseModel):
    hub_mode: str = Field(..., alias="hub.mode")
    hub_challenge: str = Field(..., alias="hub.challenge")
    hub_token: str = Field(..., alias="hub.verify_token")


async def send_hub_request(self, url, mode, token=None):
    pass


class Subscriber:
    async def validate(self, validation: Validation):
        pass


def get_subscriber() -> Subscriber:
    return Subscriber()
