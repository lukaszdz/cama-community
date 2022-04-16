""" Basic test to check the app boots up as part of CI/CD """

import os
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(
        os.environ,
        {
            "REDIS_URL": "redis://",
        },
    ):
        yield


def test_read_main():
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200

    message = response.json()["message"]
    is_healthy = message == "Systems online."

    assert is_healthy
