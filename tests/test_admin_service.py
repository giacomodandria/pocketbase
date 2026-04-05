from pytest_httpx import HTTPXMock

from pocketbase import PocketBase
from pocketbase.models.admin import Admin


def test_admin_create_uses_superusers_records_endpoint(httpx_mock: HTTPXMock):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/collections/_superusers/records",
        method="POST",
        json={
            "id": "su_123",
            "email": "root@example.com",
            "avatar": 8,
        },
    )

    admin = client.admins.create(
        {
            "email": "root@example.com",
            "password": "secret123",
            "passwordConfirm": "secret123",
            "avatar": 8,
        }
    )

    assert isinstance(admin, Admin)
    assert admin.id == "su_123"
    assert admin.email == "root@example.com"


def test_admin_auth_with_password_uses_superusers_auth_endpoint(
    httpx_mock: HTTPXMock,
):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/collections/_superusers/auth-with-password",
        method="POST",
        json={
            "token": "header.payload.signature",
            "record": {
                "id": "su_123",
                "email": "root@example.com",
                "avatar": 8,
            },
        },
    )

    result = client.admins.auth_with_password("root@example.com", "secret123")

    assert result.token == "header.payload.signature"
    assert isinstance(result.admin, Admin)
    assert result.admin.id == "su_123"
    assert client.auth_store.model is not None
    assert isinstance(client.auth_store.model, Admin)


def test_admin_auth_refresh_accepts_record_payload(httpx_mock: HTTPXMock):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/collections/_superusers/auth-refresh",
        method="POST",
        json={
            "token": "new.token.value",
            "record": {
                "id": "su_123",
                "email": "root@example.com",
                "avatar": 9,
            },
        },
    )

    result = client.admins.auth_refresh()

    assert result.token == "new.token.value"
    assert result.admin.avatar == 9
