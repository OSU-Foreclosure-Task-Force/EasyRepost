import asyncio

from tests import async_client_with_lifespan
import pytest


@pytest.mark.parametrize('async_client_with_lifespan', ['test_download_dbs/test_new_download.db'], indirect=True)
@pytest.mark.asyncio
async def test_new_download(async_client_with_lifespan):
    response = await async_client_with_lifespan.post('/download/sync/', json={
        'name': 'test',
        'url': 'https://www.youtube.com/watch?v=tHZT0GGV-2w',
        'site': 'youtube'
    })
    print(response.json())
    assert response.json()['success'] is True
    assert response.json()['payload']['id'] == 1