from event import subscribe, unsubscribe
from models.SubscriptionModels import Validation, Subscription, Hub, NewSubscription
from handler.Subscriber import Subscriber, WebSubSubscriber
from handler.Subscribers import get_subscriber, has_subscriber, get_websub_subscriber
from typing import Callable, Awaitable
from DAO import delete_hub
from config import ENABLE_AUTO_SUBSCRIPTION


class SubscriptionAPI:
    def __init__(self,
                 get_subscription: Callable[[int], Awaitable[Subscription]],
                 subscribe: Callable[[Subscription], Awaitable[bool]],
                 has_subscriber: Callable[[str], bool],
                 subscriber_factory: Callable[[str], Subscriber],
                 websub_subscriber_factory: Callable[[str], WebSubSubscriber],
                 unsubscribe: Callable[[Subscription], Awaitable[bool]],
                 get_all_hubs: Callable[[], Awaitable[list[Hub]]],
                 get_hub_info: Callable[[int], Awaitable[Hub]],
                 add_hub: Callable[[Hub], Awaitable[Hub]],
                 edit_hub_info: Callable[[Hub], Awaitable[Hub]],
                 delete_hub: Callable[[int], Awaitable[bool]],
                 ):
        self._get_subscription = get_subscription
        self._subscribe = subscribe
        self._has_subscriber = has_subscriber
        self._subscriber_factory = subscriber_factory
        self._websub_subscriber_factory = websub_subscriber_factory
        self._unsubscribe = unsubscribe
        self._get_all_hubs = get_all_hubs
        self._get_hub = get_hub_info
        self._add_hub = add_hub
        self._edit_hub_info = edit_hub_info
        self._delete_hub = delete_hub

    async def get_subscription(self, id: int) -> Subscription:
        return await self._get_subscription(id)

    async def subscribe(self, subscription: NewSubscription) -> bool:
        return await self._subscribe(subscription)

    async def subscribe_sync(self, subscription: NewSubscription) -> Subscription:
        subscriber = self._subscriber_factory(subscription.site)
        return await subscriber.subscribe(subscription)

    async def unsubscribe(self, id: int) -> bool:
        subscription = await Subscription.get(id)
        return await self._unsubscribe(subscription)

    async def validation(self, id: int, site: str, validation: Validation) -> bool:
        subscriber = self._websub_subscriber_factory(site)
        return await subscriber.validate(id,validation)

    async def receive_update(self, site: str, xml_string: str) -> bool:
        subscriber = self._subscriber_factory(site)
        return await subscriber.receive_update(xml_string)

    async def get_all_hubs(self) -> list[Hub]:
        return await self._get_all_hubs()

    async def get_hub(self, id: int) -> Hub:
        return await self._get_hub(id)

    async def add_hub(self, hub: Hub) -> Hub:
        return await self._add_hub(hub)

    async def edit_hub_info(self, hub: Hub) -> Hub:
        return await self._edit_hub_info(hub)

    async def delete_hub(self, id: int) -> bool:
        return await self._delete_hub(id)


def get_sub_api() -> SubscriptionAPI:
    if not ENABLE_AUTO_SUBSCRIPTION:
        raise NotImplementedError("Auto subscription is disabled")
    return SubscriptionAPI(
        get_subscription=Subscription.get,
        subscribe=subscribe.emit,
        has_subscriber=has_subscriber,
        subscriber_factory=get_subscriber,
        websub_subscriber_factory=get_websub_subscriber,
        unsubscribe=unsubscribe.emit,
        get_all_hubs=Hub.get_multiple,
        get_hub_info=Hub.get,
        add_hub=lambda hub: Hub.create(**hub.to_dict()),
        edit_hub_info=lambda hub: Hub.update(**hub.to_dict()),
        delete_hub=delete_hub,
    )
