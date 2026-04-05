import json

from pytest_httpx import HTTPXMock

from pocketbase import PocketBase
from pocketbase.models.record import Record


def test_request_otp(httpx_mock: HTTPXMock):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/collections/users/request-otp",
        method="POST",
        json={"otpId": "otp_123"},
    )

    result = client.collection("users").request_otp("user@example.com")

    assert result == {"otpId": "otp_123"}


def test_auth_with_otp_updates_auth_store(httpx_mock: HTTPXMock):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/collections/users/auth-with-otp",
        method="POST",
        json={
            "token": "header.payload.signature",
            "record": {
                "id": "user_123",
                "collectionId": "users",
                "collectionName": "users",
                "email": "user@example.com",
            },
        },
    )

    result = client.collection("users").auth_with_otp("otp_123", "123456")

    assert result.token == "header.payload.signature"
    assert isinstance(result.record, Record)
    assert result.record.id == "user_123"
    assert client.auth_store.token == "header.payload.signature"
    assert client.auth_store.model is not None
    assert client.auth_store.model.id == "user_123"


def test_impersonate_includes_duration(httpx_mock: HTTPXMock):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/collections/users/impersonate/user_123",
        method="POST",
        json={
            "token": "header.payload.signature",
            "record": {
                "id": "user_123",
                "collectionId": "users",
                "collectionName": "users",
            },
        },
    )

    result = client.collection("users").impersonate("user_123", duration=60)

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"
    assert request.url.path == "/api/collections/users/impersonate/user_123"
    assert json.loads(request.content) == {"duration": 60}
    assert result.record.id == "user_123"
