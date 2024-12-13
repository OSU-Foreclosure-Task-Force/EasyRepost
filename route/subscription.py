from fastapi import APIRouter, Depends
from API.subscription import get_sub_api, SubscriptionAPI, Validation


class SubscriptionRoute:
    def __init__(self, subscription_api: SubscriptionAPI = Depends(get_sub_api)):
        self._api = subscription_api

    def register_to_router(self, router: APIRouter):
        router.add_api_route("/", self.subscribe, methods=["POST"])
        router.add_api_route("/", self.unsubscribe, methods=["DELETE"])
        router.add_api_route("/callback", self.validation, methods=["GET"])
        router.add_api_route("/callback", self.receive_update, methods=["POST"])
        router.add_api_route("/hub", self.get_all_hubs, methods=["GET"])
        router.add_api_route("/hub/{id}", self.get_hub_info, methods=["GET"])
        router.add_api_route("/hub/{id}", self.add_hub, methods=["POST"])
        router.add_api_route("/hub/{id}", self.edit_hub_info, methods=["PUT"])
        router.add_api_route("/hub/{id}", self.delete_hub, methods=["DELETE"])

    async def subscribe(self, params):
        """Subscribe to a topic using the provided parameters"""
        return await self._api.subscribe(params)

    async def unsubscribe(self, params):
        """Unsubscribe from a topic using the provided parameters"""
        return await self._api.unsubscribe(params)

    async def validation(self, params: Validation):
        """Validate a subscription request"""
        return await self._api.validation(params)

    async def receive_update(self, params):
        """Handle updates received from a topic"""
        return await self._api.receive_update(params)

    async def get_all_hubs(self):
        """Retrieve all available hubs"""
        return await self._api.get_all_hubs()

    async def get_hub_info(self, id: int):
        """Retrieve information about a specific hub by its ID"""
        return await self._api.get_hub_info(id)

    async def add_hub(self, hub_info):
        """Add a new hub with the provided information"""
        return await self._api.add_hub(hub_info)

    async def edit_hub_info(self, id: int, hub_info):
        """Edit the information of an existing hub by its ID"""
        return await self._api.edit_hub_info(id, hub_info)

    async def delete_hub(self, id: int):
        """Delete a hub by its ID"""
        return await self._api.delete_hub(id)


subscription_router = APIRouter(prefix="/subscription")
# 注册路由
subscription_route = SubscriptionRoute()
subscription_route.register_to_router(subscription_router)
