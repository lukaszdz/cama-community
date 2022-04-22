""" Basic test to check the app boots up as part of CI/CD """

import os
from unittest import mock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(
        os.environ,
        {
            "REDIS_URL": "redis://",
            "AUDIO_ENABLED": "0",
            "DISCORD_BOT_TOKEN": "this-is-a-mock-token",
            "BOT_COMMAND_PREFIX": "?",
            "DISCORD_LOGGING_CHANNEL": "13333333333337",
            "ENV": "test",
        },
    ):
        yield


def test_read_main():
    from main import api

    client = TestClient(api)

    response = client.get("/")
    assert response.status_code == 200

    message = response.json()["message"]
    is_healthy = message == "Systems online."

    assert is_healthy
