from pydantic import BaseModel, Field


class ValidationParams(BaseModel):
    hub_mode: str = Field(..., alias="hub.mode")
    hub_challenge: str = Field(..., alias="hub.challenge")
    hub_token: str = Field(..., alias="hub.verify_token")


class SubscribeParams(BaseModel):
    hub_name: str = Field(...)
    topic_url: str = Field(...)
    mode: str = Field(...)


class UnsubscribeParams:
    pass


class UpdateParams(BaseModel):
    pass


class HubInfo(BaseModel):
    pass


class SubscriptionAPI:
    async def subscribe(self, params: SubscribeParams):
        pass

    async def unsubscribe(self, params: UnsubscribeParams):
        pass

    async def validation(self, params: ValidationParams):
        pass

    async def receive_update(self, params: UpdateParams):
        pass

    async def get_all_hubs(self):
        pass

    async def get_hub_info(self, id: int):
        pass

    async def add_hub(self, hub_info: HubInfo):
        pass

    async def edit_hub_info(self, id: int, hub_info: HubInfo):
        pass

    async def delete_hub(self, id: int):
        pass


def get_sub_api() -> SubscriptionAPI:
    return SubscriptionAPI()
