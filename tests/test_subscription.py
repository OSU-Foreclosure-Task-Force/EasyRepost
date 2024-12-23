from fastapi.testclient import TestClient
from httpx import Response
from tests import sync_client, async_client
import pytest
import asyncio
import json


def post_add_hub(sync_client: TestClient, name: str, url: str) -> Response:
    response = sync_client.post('/subscription/hub', json={
        'name': name,
        'url': url,
    })
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['success'] is True
    payload = response_data["payload"]
    assert payload['name'] == name
    assert payload['url'] == url
    assert isinstance(payload['id'], int)
    return response


def get_all_hubs(sync_client: TestClient) -> Response:
    response = sync_client.get('/subscription/hub')
    response_data = response.json()
    assert response_data['success'] is True
    assert isinstance(response_data['payloads'], list)
    return response


def get_hub(sync_client: TestClient, id: int) -> Response:
    response = sync_client.get(f'/subscription/hub/{id}')
    response_data = response.json()
    assert response_data['success'] is True
    assert response_data['payload'] is not None
    return response


def delete_hub(sync_client: TestClient, id: int) -> Response:
    response = sync_client.delete(f'/subscription/hub/{id}')
    response_data = response.json()
    assert response_data['success'] is True
    return response


def edit_hub_name(sync_client: TestClient, id: int, name: str) -> Response:
    response = sync_client.put(f'/subscription/hub/{id}', json={
        'name': name,
    })
    response_data = response.json()
    print(response_data)
    assert response_data['success'] is True
    payload = response_data["payload"]
    assert payload['name'] == name
    assert payload['id'] == id
    return response


@pytest.mark.parametrize('sync_client', ['test_subscription_dbs/test_crud_hub.db'], indirect=True)
def test_crud_hub(sync_client):
    first_hub_name = 'test_hub'
    first_hub_url = "https://example.com"
    add_hub_response = post_add_hub(sync_client, first_hub_name, first_hub_url)
    first_new_hub_id = add_hub_response.json()['payload']['id']

    second_hub_name = 'test_hub_second'
    second_hub_url = "https://exampleSecond.com"
    add_hub_response = post_add_hub(sync_client, second_hub_name, second_hub_url)
    second_hub_id = add_hub_response.json()['payload']['id']

    get_all_hubs_response = get_all_hubs(sync_client)
    assert len(get_all_hubs_response.json()['payloads']) == 2

    get_first_hub_response = get_hub(sync_client, first_new_hub_id)
    assert get_first_hub_response.json()['payload']['name'] == first_hub_name
    assert get_first_hub_response.json()['payload']['url'] == first_hub_url

    get_second_hub_response = get_hub(sync_client, second_hub_id)
    assert get_second_hub_response.json()['payload']['name'] == second_hub_name
    assert get_second_hub_response.json()['payload']['url'] == second_hub_url

    second_hub_name_new = 'new_hub_name'
    edit_second_hub_response = edit_hub_name(sync_client, second_hub_id, second_hub_name_new)
    edited_second_hub_name = edit_second_hub_response.json()['payload']['name']
    assert edited_second_hub_name == second_hub_name_new
    assert edited_second_hub_name != second_hub_name
    assert edit_second_hub_response.json()['payload']['url'] == second_hub_url

    delete_hub(sync_client, first_new_hub_id)
    get_all_hubs_response = get_all_hubs(sync_client)
    assert len(get_all_hubs_response.json()['payloads']) == 1


@pytest.mark.parametrize('async_client', ['test_subscription_dbs/test_subscribe.db'], indirect=True)
@pytest.mark.asyncio
async def test_subscribe_sync(httpx_mock, async_client):
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
    post_sub = asyncio.create_task(async_client.post(url='/subscription/sync', json={
        "site": SITE,
        "hub_id": HUB_ID,
        "topic_uri": TOPIC_URI + TEST_CHANNEL
    }))
    # wait for server subscription request to YouTube hub
    await asyncio.sleep(0.05)
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

    post_validation = asyncio.create_task(async_client.get(url=SERVER_CALLBACK, params={
        "hub.challenge": CHALLENGE,
        "hub.topic": SERVER_TOPIC_URL,
        "hub.verify_token": TOKEN,
        "hub.mode": SERVER_MODE
    }))
    validation_response = await post_validation

    assert validation_response.json()["hub.challenge"] == CHALLENGE

    response = await post_sub
    data = response.json()
    assert isinstance(data["payload"]["id"], int)
    assert data["payload"]["hub_id"] == HUB_ID
    assert data["payload"]["topic_uri"] == TOPIC_URI + TEST_CHANNEL
