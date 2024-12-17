from event import subscribe, unsubscribe
from model import Subscription, Hub
from handler.Subscriber import Validation, Subscriber, get_subscriber
from event.Events import Feed
from event import channel_update
from typing import Callable, Awaitable


class SubscriptionAPI:
    def __init__(self,
                 subscriber: Subscriber,
                 subscribe_task: Callable[[Subscription], Awaitable[bool]],
                 unsubscribe_task: Callable[[Subscription], Awaitable[bool]],
                 receive_update_task: Callable[[Feed], Awaitable[bool]],
                 get_all_hubs_task: Callable[[], Awaitable[list[Hub]]],
                 get_hub_info_task: Callable[[int], Awaitable[dict]],
                 add_hub_task: Callable[[Hub], Awaitable[Hub]],
                 edit_hub_info_task: Callable[[Hub], Awaitable[Hub]],
                 delete_hub_task: Callable[[int], Awaitable[bool]]
                 ):
        self._subscriber = subscriber
        self._subscribe_task = subscribe_task
        self._unsubscribe_task = unsubscribe_task
        self._receive_update_task = receive_update_task
        self._get_all_hubs_task = get_all_hubs_task
        self._get_hub_info_task = get_hub_info_task
        self._add_hub_task = add_hub_task
        self._edit_hub_info_task = edit_hub_info_task
        self._delete_hub_task = delete_hub_task

    async def subscribe(self, subscription: Subscription) -> bool:
        return await self._subscribe_task(subscription)

    async def unsubscribe(self, id: int) -> bool:
        subscription = await Subscription.get(id)
        return await self._unsubscribe_task(subscription)

    async def validation(self, validation: Validation) -> bool:
        return await self._subscriber.validate(validation)

    async def receive_update(self, feed: Feed) -> bool:
        return await self._receive_update_task(feed)

    async def get_all_hubs(self) -> list[Hub]:
        return await self._get_all_hubs_task()

    async def get_hub_info(self, id: int) -> dict:
        return await self._get_hub_info_task(id)

    async def add_hub(self, hub: Hub) -> Hub:
        return await self._add_hub_task(hub)

    async def edit_hub_info(self, hub: Hub) -> Hub:
        return await self._edit_hub_info_task(hub)

    async def delete_hub(self, id: int) -> bool:
        return await self._delete_hub_task(id)


def get_sub_api() -> SubscriptionAPI:
    return SubscriptionAPI(
        get_subscriber(),
        subscribe.emit,
        unsubscribe.emit,
        channel_update.emit,
        Hub.get_multiple,
        Hub.get,
        lambda hub: Hub.create(**hub.to_dict()),
        lambda hub: Hub.update(**hub.to_dict()),
        Hub.delete,
    )
