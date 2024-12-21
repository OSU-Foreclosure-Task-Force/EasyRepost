import asyncio
import datetime
from event import new_download, feed_broadcast, subscribe_complete, unsubscribe_complete
from event.Event import Event
from config import SUBSCRIPTION_TOKEN, CALL_BACK_URL, VALIDATION_INTERVAL
from models.SubscriptionModels import Validation, NewSubscription, Feed, Subscription, Hub, FeedXML
from models.TaskModels import NewDownloadTask
import httpx
import secrets
from xml.etree.ElementTree import ElementTree, fromstring

class Subscriber:
    def __init__(self,
                 subscribe_complete_event: Event = subscribe_complete,
                 unsubscribe_complete_event: Event = unsubscribe_complete,
                 new_download_event: Event = new_download,
                 new_feed_event: Event = feed_broadcast):
        self.subscribe_complete = subscribe_complete_event
        self.unsubscribe_complete = unsubscribe_complete_event
        self.new_download_event = new_download_event
        self.new_feed_event = new_feed_event

    @staticmethod
    def get_xml_root(raw_xml: str) -> ElementTree:
        return ElementTree(fromstring(raw_xml))

    async def subscribe(self, subscription: NewSubscription, secret: str = secrets.token_hex()) -> Subscription:
        no_secret_sub = await Subscription.create(**subscription.model_dump())
        no_secret_sub.secret = secret
        secret_sub = await Subscription.update(**no_secret_sub.to_dict())
        return secret_sub

    async def unsubscribe(self, id: int) -> Subscription:
        subscription = await Subscription.get(id)
        await Subscription.delete(id)
        return subscription

    async def receive_update(self, xml_string: str) -> bool:
        xml_tree = self.get_xml_root(xml_string)
        feed = await self.parse_xml_to_feed(xml_tree)
        self.new_feed_event.emit(feed)
        task = self.parse_feed_to_download_task(feed)
        await FeedXML.create(xml=xml_string)
        return self.new_download_event.emit(task)

    async def parse_xml_to_feed(self, xml: ElementTree) -> Feed:
        raise NotImplementedError

    async def parse_feed_to_download_task(self, feed: Feed) -> NewDownloadTask:
        raise NotImplementedError


class RSSSubscriber(Subscriber):
    def __init__(self, new_download_event: Event = new_download):
        super().__init__(new_download_event)
        self._subscriptions: dict[int, Subscription] = {}
        self._polling_tasks: dict[int, asyncio.Task] = {}

    async def _polling(self, url: str, sub_id: int):
        try:
            while True:
                raw_xml = await self.get_update(url)
                await self.receive_update(raw_xml)
                sub = await Subscription.get(sub_id)
                await asyncio.sleep(sub.polling_interval)
        except asyncio.CancelledError:
            return

    async def load_subscriptions(self):
        subscriptions = await Subscription.get_multiple()
        self._subscriptions = {subscription.id: subscription for subscription in subscriptions}

    async def create_polling_task(self, subscription: Subscription):
        hub = await Hub.get(subscription.hub_id)
        self._polling_tasks[subscription.id] = asyncio.create_task(self._polling(url=hub.url, sub_id=subscription.id))

    async def start_polling(self):
        for subscription in self._subscriptions.values():
            await self.create_polling_task(subscription)

    async def subscribe(self, subscription: NewSubscription, secret: str = secrets.token_hex()) -> Subscription:
        persisted_subscription = await super().subscribe(subscription)
        await self.create_polling_task(persisted_subscription)
        self.subscribe_complete.emit(persisted_subscription)
        return persisted_subscription

    async def unsubscribe(self, id: int) -> Subscription:
        subscription = await super().unsubscribe(id)
        self._polling_tasks[id].cancel()
        del self._polling_tasks[id]
        self.unsubscribe_complete.emit(subscription)
        return subscription

    @staticmethod
    async def get_update(url: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.text


class WebSubSubscriber(Subscriber):
    def __init__(self,
                 subscribe_complete_event: Event = subscribe_complete,
                 unsubscribe_complete_event: Event = unsubscribe_complete,
                 new_download_event: Event = new_download,
                 new_feed_event: Event = feed_broadcast):
        super().__init__(subscribe_complete_event, unsubscribe_complete_event, new_download_event, new_feed_event)
        self._validation_sessions: dict[int, asyncio.Task] = {}

    async def validate(self, id: int, validation: Validation) -> bool:
        if validation.hub_token == SUBSCRIPTION_TOKEN:
            self._validation_sessions[id].cancel()
        return validation.hub_token == SUBSCRIPTION_TOKEN

    @staticmethod
    async def _send_subscription_request(subscribe: bool, hub: Hub, subscription: NewSubscription, secret: str,
                                         id: int):
        async with httpx.AsyncClient() as client:
            lease_number_delta = subscription.lease_time - datetime.datetime.now()
            lease_number = lease_number_delta.total_seconds()
            body = {
                "hub.callback": CALL_BACK_URL + '/subscription/callback/' + subscription.site + f'/{id}',
                "hub.topic": subscription.topic_uri,
                "hub.verify": "async",
                "hub.mode": "subscribe" if subscribe else "unsubscribe",
                "hub.verify_token": SUBSCRIPTION_TOKEN,
                "hub.lease_numbers": lease_number if lease_number > 0 else None,
                "hub.secret": secret
            }
            response = await client.post(hub.url, json=body)
            if response.is_error:
                raise RuntimeError(f'Hub {hub.name} responded with an error'
                                   f'Hub url: {hub.url}'
                                   f'error info:{response.text}')

    def wait_validation(self, id: int, validation_interval: int = VALIDATION_INTERVAL) -> asyncio.Task:
        self._validation_sessions[id] = asyncio.create_task(asyncio.sleep(validation_interval))
        return self._validation_sessions[id]

    async def subscribe(self, subscription: NewSubscription, secret: str = secrets.token_hex()) -> Subscription:
        hub = await Hub.get(subscription.hub_id)
        persisted_subscription = await super().subscribe(subscription, secret)
        await self._send_subscription_request(True, hub, subscription, secret, persisted_subscription.id)
        success = False
        try:
            await self.wait_validation(persisted_subscription.id)
        except asyncio.CancelledError:
            success = True
        finally:
            del self._validation_sessions[persisted_subscription.id]
        if not success:
            await Subscription.delete(persisted_subscription.id)
            raise RuntimeError(f'Subscribe failed, detail: {persisted_subscription.to_dict()}')
        self.subscribe_complete.emit(persisted_subscription)
        return persisted_subscription

    async def unsubscribe(self, id: int) -> Subscription:
        subscription = await super().unsubscribe(id)
        hub = await Hub.get(subscription.hub_id)
        await self._send_subscription_request(False, hub, subscription, subscription.secret, subscription.id)
        self.unsubscribe_complete.emit(subscription)
        return subscription

    async def compare_signature(self, secret: str, body: bytes, signature: str) -> bool:
        raise NotImplementedError
