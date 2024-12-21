import os.path
from fastapi.testclient import TestClient
import importlib
import pytest


def generate_path(db_name: str):
    return os.path.join(os.getcwd(), db_name)


@pytest.fixture(scope='function')
def client(request) -> TestClient:
    db_name = request.param
    db_path = generate_path(db_name)
    if db_name is None:
        db_path = ":memory:"
    import config

    saved_db_path = config.config["Database"]["sqlite_path"]
    config.config["Database"]["sqlite_path"] = db_path
    config.write_back()
    with open(db_path, 'rb') as f:
        file = f.read()

    importlib.reload(config)
    import database
    importlib.reload(database)
    import model
    importlib.reload(model)
    import server
    importlib.reload(server)
    client = TestClient(server.app)

    yield client

    with open(db_path, 'wb') as f:
        f.write(file)
    config.config["Database"]["sqlite_path"] = saved_db_path
    config.write_back()
