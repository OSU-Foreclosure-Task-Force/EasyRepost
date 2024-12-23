from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from cryptography.fernet import Fernet
from config import WEB_HUB_SECRET_KEY
from model import BaseWithUtils, DataResponse, DataListResponse


# pydantic models (can be used for param parsing)

class Validation(BaseModel):
    hub_mode: str = Field(validation_alias="hub.mode")
    hub_topic: str = Field(validation_alias="hub.topic")
    hub_challenge: str = Field(validation_alias="hub.challenge")
    hub_token: str | None = Field(None, validation_alias="hub.verify_token")
    hub_lease_seconds: str | None = Field(None, validation_alias="hub.lease_seconds")


class ValidationResponse(BaseModel):
    hub_challenge: str = Field(serialization_alias="hub.challenge")


class Feed(BaseModel):
    video_id: str
    video_title: str
    video_url: str
    channel_id: str
    channel_title: str
    channel_url: str
    site: str
    update_time: datetime = datetime.now()

    class Config:
        extra = 'allow'

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class NewHub(BaseModel):
    name: str
    url: str


class PersistedHub(NewHub):
    id: int


class PersistedHubResponse(DataResponse):
    payload: PersistedHub


class PersistedHubListResponse(DataListResponse):
    payloads: list[PersistedHub]


class EditHub(BaseModel):
    name: str = Field(None)
    url: str = Field(None)


class NewSubscription(BaseModel):
    site: str
    hub_id: int
    topic_uri: str
    lease_time: datetime = Field(datetime.now())


class PersistedSubscription(NewSubscription):
    id: int
    time: datetime
    encrypted_secret: str
    polling_interval: int | None = Field(None)


class PersistedSubscriptionResponse(DataResponse):
    payload: PersistedSubscription


# SQL ORM Models


class Subscription(BaseWithUtils):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    site = Column(String, default=None)
    hub_id = Column(Integer, ForeignKey("hubs.id"), index=True)
    topic_uri = Column(String, default=None)
    polling_interval = Column(Integer, default=None)
    time = Column(DateTime, default=datetime.now())
    lease_time = Column(DateTime, default=datetime.now())
    encrypted_secret = Column(String, default=None)

    @property
    def pydantic(self):
        return PersistedSubscription(**self.to_dict())

    @property
    def secret(self):
        cipher = Fernet(WEB_HUB_SECRET_KEY)
        decrypted = cipher.decrypt(self.encrypted_secret.encode())
        return decrypted.decode()

    @secret.setter
    def secret(self, new_secret: str):
        cipher = Fernet(WEB_HUB_SECRET_KEY)
        encrypted = cipher.encrypt(new_secret.encode())
        self.encrypted_secret = encrypted.decode()


class Hub(BaseWithUtils):
    __tablename__ = "hubs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(16), default=None)
    url = Column(String(128), default=None)

    @property
    def pydantic(self):
        return PersistedHub(**self.to_dict())


class FeedXML(BaseWithUtils):
    __tablename__ = "feed_xmls"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    download_task_id = Column(Integer, ForeignKey("download_tasks.id"), index=True)
    xml = Column(Text)
