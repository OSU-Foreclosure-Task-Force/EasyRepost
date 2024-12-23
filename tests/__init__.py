import os.path
from fastapi.testclient import TestClient
import importlib
import pytest
import config
import database
import model
import DAO
import server
from httpx import ASGITransport, AsyncClient
import pytest_asyncio


def generate_path(db_name: str):
    return os.path.join(os.getcwd(), db_name)


def db_setup(db_name):
    db_path = generate_path(db_name)
    if db_name is None:
        db_path = ":memory:"
    import config

    saved_db_path = config.config["Database"]["sqlite_path"]
    config.config["Database"]["sqlite_path"] = db_path
    config.write_back()
    with open(db_path, 'rb') as f:
        db_file = f.read()

    importlib.reload(config)
    importlib.reload(database)
    importlib.reload(model)
    importlib.reload(DAO)
    importlib.reload(server)
    return saved_db_path, db_file


def db_teardown(saved_db_path, cur_db_path, db_file):
    with open(cur_db_path, 'wb') as f:
        f.write(db_file)
    config.config["Database"]["sqlite_path"] = saved_db_path
    config.write_back()


@pytest.fixture(scope='function')
def sync_client(request) -> TestClient:
    saved_db_path, db_file = db_setup(request.param)
    client = TestClient(server.app)
    yield client
    db_teardown(saved_db_path, request.param, db_file)


@pytest_asyncio.fixture(scope='function')
async def async_client(request) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=server.app), base_url="http://test") as client:
        saved_db_path, db_file = db_setup(request.param)
        yield client
        db_teardown(saved_db_path, request.param, db_file)
