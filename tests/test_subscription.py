from fastapi.testclient import TestClient
from httpx import Response
from tests import client
import pytest
import asyncio
import json


def post_add_hub(client: TestClient, name: str, url: str) -> Response:
    return client.post('/subscription/hub', json={
        'name': name,
        'url': url,
    })


@pytest.mark.parametrize('client', ['subscription_test_dbs/add_hub.db'], indirect=True)
def test_add_hub(client):
    NAME = 'test_hub'
    URL = "https://example.com"
    response = post_add_hub(client, NAME, URL)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['success'] is True
    assert response_data['message'] == 'Action completed successfully'
    payload = response_data["payload"]
    assert payload['name'] == NAME
    assert payload['url'] == URL
    assert isinstance(payload['id'], int)


@pytest.mark.parametrize('client', ['subscription_test_dbs/subscribe_test.db'], indirect=True)
@pytest.mark.asyncio
async def test_subscribe_sync(httpx_mock, client):
    httpx_mock.add_response(
        method="POST",
        url="https://testhub.com/subscribe",
        status_code=200,
    )

    SITE = "youtube"
    HUB_ID = 1
    TOPIC_URI = "https://www.youtube.com/feeds/videos.xml?channel_id="
    TEST_CHANNEL = "UCgWN9tTX3GGHd0_dGAP1ECA"
    # user post subscribe request
    post_sub = asyncio.to_thread(client.post, url='/subscription/sync', json={
        "site": SITE,
        "hub_id": HUB_ID,
        "topic_uri": TOPIC_URI + TEST_CHANNEL
    })
    post_sub_task = asyncio.create_task(post_sub)
    # wait for server subscription request to YouTube hub
    await asyncio.sleep(2)
    requests = httpx_mock.get_requests()
    request = requests[0]
    CONTENT = request.content.decode()
    JSON = json.loads(CONTENT)
    # mock challenge request from YouTube hub
    CHALLENGE = "test_challenge"
    TOKEN = JSON['hub.verify_token']
    SERVER_TOPIC_URL = JSON["hub.topic"]
    SERVER_CALLBACK = JSON["hub.callback"]
    SERVER_MODE = JSON["hub.mode"]

    assert "hub.secret" in JSON
    assert SERVER_TOPIC_URL == TOPIC_URI + TEST_CHANNEL
    assert SERVER_MODE == "subscribe"

    post_validation = asyncio.to_thread(client.get, url=SERVER_CALLBACK, params={
        "hub.challenge": CHALLENGE,
        "hub.topic": SERVER_TOPIC_URL,
        "hub.verify_token": TOKEN,
        "hub.mode": SERVER_MODE
    })
    post_validation_task = asyncio.create_task(post_validation)
    validation_response = await post_validation_task

    assert validation_response.json()["hub.challenge"] == CHALLENGE

    response = await post_sub_task
    data = response.json()
    assert isinstance(data["payload"]["id"], int)
    assert data["payload"]["hub_id"] == HUB_ID
    assert data["payload"]["topic_uri"] == TOPIC_URI + TEST_CHANNEL