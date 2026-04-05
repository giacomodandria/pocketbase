import json

from pytest_httpx import HTTPXMock

from pocketbase import PocketBase


def test_generate_apple_client_secret(httpx_mock: HTTPXMock):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/settings/apple/generate-client-secret",
        method="POST",
        json={"secret": "eyJhbGciOiJFUzI1NiJ9.test.signature"},
    )

    result = client.settings.generate_apple_client_secret(
        client_id="com.example.app",
        team_id="TEAM123",
        key_id="KEY456",
        private_key="-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----",
        duration=15780000,
    )

    request = httpx_mock.get_request()
    assert request is not None
    body = json.loads(request.content)
    assert body["clientId"] == "com.example.app"
    assert body["teamId"] == "TEAM123"
    assert body["keyId"] == "KEY456"
    assert body["duration"] == 15780000
    assert result == "eyJhbGciOiJFUzI1NiJ9.test.signature"
