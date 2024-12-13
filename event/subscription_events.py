from event.Event import Event
from model import Subscription


class SubscriptionEvent(Event):
    def emit(self, subscription: Subscription) -> bool:
        return super().emit(subscription)
