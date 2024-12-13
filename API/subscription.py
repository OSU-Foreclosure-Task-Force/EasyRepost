from event import subscribe, unsubscribe
from model import Subscription, Hub
from handler.Subscriber import Validation, Subscriber
from event.channel_events import Feed
from event import channel_update


class SubscriptionAPI:

    @staticmethod
    async def subscribe(subscription: Subscription) -> bool:
        return subscribe.emit(subscription)

    @staticmethod
    async def unsubscribe(id: int) -> bool:
        subscription = await Subscription.get(id)
        return unsubscribe.emit(subscription)

    @staticmethod
    async def validation(validation: Validation, subscriber: Subscriber) -> dict:
        return await subscriber.validate(validation)

    @staticmethod
    async def receive_update(feed: Feed) -> bool:
        return channel_update.emit(feed)

    @staticmethod
    async def get_all_hubs() -> list[Hub]:
        return await Hub.get_multiple()

    @staticmethod
    async def get_hub_info(id: int) -> dict:
        return await Hub.get(id).to_dict

    @staticmethod
    async def add_hub(hub: Hub):
        return await Hub.create(**hub.to_dict())

    @staticmethod
    async def edit_hub_info(id: int, hub: Hub):
        return await Hub.update(id, **hub.to_dict())

    @staticmethod
    async def delete_hub(id: int):
        return await Hub.delete(id)


def get_sub_api() -> SubscriptionAPI:
    return SubscriptionAPI()
