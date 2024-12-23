from fastapi import APIRouter, Request, HTTPException, Query
from API.subscription import get_sub_api, SubscriptionAPI
from models.SubscriptionModels import (Validation,
                                       Hub,
                                       NewHub,
                                       NewSubscription,
                                       EditHub,
                                       PersistedSubscriptionResponse,
                                       ValidationResponse,
                                       PersistedHubListResponse,
                                       PersistedHubResponse)
from model import BaseResponse
from handler.Subscribers import get_websub_subscriber
from typing import Annotated

class SubscriptionRoute:
    def __init__(self, subscription_api: SubscriptionAPI = get_sub_api()):
        self._api = subscription_api

    def register_to_router(self, router: APIRouter):
        router.add_api_route("/", self.subscribe, methods=["POST"])
        router.add_api_route("/sync", self.subscribe_sync, methods=["POST"])
        router.add_api_route("/", self.unsubscribe, methods=["DELETE"])
        router.add_api_route("/callback/{site}/{id}", self.validation, methods=["GET"])
        router.add_api_route("/callback/{site}/{id}", self.receive_update, methods=["POST"])
        router.add_api_route("/hub", self.get_all_hubs, methods=["GET"])
        router.add_api_route("/hub", self.add_hub, methods=["POST"])
        router.add_api_route("/hub/{id}", self.get_hub, methods=["GET"])
        router.add_api_route("/hub/{id}", self.edit_hub_info, methods=["PUT"])
        router.add_api_route("/hub/{id}", self.delete_hub, methods=["DELETE"])

    async def subscribe(self, subscription: NewSubscription) -> BaseResponse:
        """Subscribe to a topic using the provided parameters"""
        success = await self._api.subscribe(subscription)
        return BaseResponse(
            success=success,
            message="subscribe successfully" if success else "failed to emit a subscribe event"
        )

    async def subscribe_sync(self, subscription: NewSubscription) -> PersistedSubscriptionResponse:
        """Subscribe to a topic using the provided parameters and return the persisted subscription"""
        persisted_subscription = await self._api.subscribe_sync(subscription)
        return PersistedSubscriptionResponse(payload=persisted_subscription.pydantic)

    async def unsubscribe(self, id: int) -> BaseResponse:
        """Unsubscribe from a topic using the provided parameters"""
        success = await self._api.unsubscribe(id)
        return BaseResponse(
            success=success,
            message="unsubscribe successfully" if success else "failed to emit a unsubscribe event"
        )

    async def validation(self, id: int, site: str, validation: Annotated[Validation,Query()]) -> ValidationResponse:
        """Validate a subscription request"""
        valid = await self._api.validation(id, site, validation)
        return ValidationResponse(hub_challenge=validation.hub_challenge if valid else "Invalid")

    async def receive_update(self, id: int, site: str, request: Request) -> BaseResponse:
        """Handle updates received from a topic"""
        subscription = await self._api.get_subscription(id)
        subscriber = get_websub_subscriber(site)
        signature = request.headers.get('X-Hub-Signature')
        if signature is None:
            raise HTTPException(400,"signature not detected")
        if not subscriber.compare_signature(subscription.secret, await request.body(), signature):
            raise HTTPException(400, "signature not valid")

        raw_xml = await request.body()
        success = await self._api.receive_update(site,raw_xml.decode())
        return BaseResponse(
            success=success,
            message="update received successfully" if success else "failed to emit an update event"
        )

    async def get_all_hubs(self) -> PersistedHubListResponse:
        """Retrieve all available hubs"""
        hubs = await self._api.get_all_hubs()
        return PersistedHubListResponse(payloads=[hub.pydantic for hub in hubs])

    async def get_hub(self, id: int) -> PersistedHubResponse:
        """Retrieve information about a specific hub by its ID"""
        hub = await self._api.get_hub(id)
        return PersistedHubResponse(payload=hub.pydantic)

    async def add_hub(self, hub: NewHub) -> PersistedHubResponse:
        """Add a new hub with the provided information"""
        new_hub = Hub(**hub.model_dump())
        persisted_hub = await self._api.add_hub(new_hub)
        return PersistedHubResponse(payload=persisted_hub.pydantic)

    async def edit_hub_info(self, id: int, hub: EditHub) -> PersistedHubResponse:
        """Edit the information of an existing hub by its ID"""
        edit_hub = Hub(id=id, **hub.model_dump(exclude_none=True))
        persisted_hub = await self._api.edit_hub_info(edit_hub)
        return PersistedHubResponse(payload=persisted_hub.pydantic)

    async def delete_hub(self, id: int) -> BaseResponse:
        """Delete a hub by its ID"""
        success = await self._api.delete_hub(id)
        return BaseResponse(
            success=success,
            message="hub deleted successfully" if success else "failed to delete hub"
        )


subscription_router = APIRouter(prefix="/subscription")
# Register routes
subscription_route = SubscriptionRoute()
subscription_route.register_to_router(subscription_router)
