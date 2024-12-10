from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from API.subscription import get_sub_api,SubscriptionAPI

subscription = APIRouter(prefix="/subscription")

class ValidationParams(BaseModel):
    hub_mode: str = Field(..., alias="hub.mode")
    hub_challenge: str = Field(..., alias="hub.challenge")
    hub_token: str = Field(...,alias="hub.verify_token")

class SubscribeParams(BaseModel):
    hub_name:str = Field(...)
    topic_url:str = Field(...)
    mode:str = Field(...)

class UnsubscribeParams:
    pass

class UpdateParams(BaseModel):
    pass

class HubInfo(BaseModel):
    pass

@subscription.post("/")
async def subscribe(params:SubscribeParams, sub_api : SubscriptionAPI = Depends(get_sub_api)):
    pass

@subscription.delete("/")
async def unsubscribe(params:SubscribeParams, sub_api : SubscriptionAPI = Depends(get_sub_api)):
    pass

@subscription.get("/callback")
async def validation(params:ValidationParams,sub_api : SubscriptionAPI = Depends(get_sub_api)):
    pass

@subscription.post("/callback")
async def receive_update(params:UpdateParams,sub_api : SubscriptionAPI = Depends(get_sub_api)):
    pass

@subscription.get("/hub")
async def get_all_hubs():
    pass

@subscription.get("/hub/{id}")
async def get_hub_info(id:int):
    pass

@subscription.post("/hub/{id}")
async def add_hub(hub_info:HubInfo):
    pass

@subscription.get("/hub/{id}")
async def edit_hub_info(id:int,hub_info:HubInfo):
    pass

@subscription.get("/hub/{id}")
async def delete_hub(id:int):
    pass