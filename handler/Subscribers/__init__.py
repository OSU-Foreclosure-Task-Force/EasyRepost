from handler.Subscriber import Subscriber, WebSubSubscriber
from .Youtube import YoutubeSubscriber
from models.SubscriptionModels import NewSubscription, PersistedSubscription
from event import subscribe, unsubscribe

__all__ = ["get_subscriber", "get_websub_subscriber", "has_subscriber"]

_subscribers: dict[str, Subscriber] = {
    "youtube": YoutubeSubscriber()
}


def get_subscriber(site: str) -> Subscriber:
    return _subscribers[site.lower()]


def get_websub_subscriber(site: str) -> WebSubSubscriber | None:
    subscriber = _subscribers[site.lower()]
    if not isinstance(subscriber, WebSubSubscriber):
        subscriber = None
    return subscriber


def has_subscriber(site: str) -> bool:
    return site in _subscribers


@subscribe.connect
async def on_subscribe(subscription: NewSubscription):
    subscriber = get_subscriber(subscription.site)
    return await subscriber.subscribe(subscription)


@unsubscribe.connect
async def on_unsubscribe(subscription: PersistedSubscription):
    subscriber = get_subscriber(subscription.site)
    return await subscriber.unsubscribe(subscription.id)
