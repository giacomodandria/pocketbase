import json

from pocketbase import PocketBase

def test_list_external_auths(httpx_mock):
    client = PocketBase("http://localhost:8090")
    
    httpx_mock.add_response(
        url="http://localhost:8090/api/collections/users/records/user_123/external-auths",
        method="GET",
        json=[
            {"id": "ea_1", "recordId": "user_123", "provider": "github", "providerId": "gh_123"},
            {"id": "ea_2", "recordId": "user_123", "provider": "google", "providerId": "go_456"}
        ],
    )

    auths = client.collection("users").list_external_auths("user_123")
    
    assert len(auths) == 2
    assert auths[0].provider == "github"
    assert auths[1].provider == "google"

def test_unlink_external_auth(httpx_mock):
    client = PocketBase("http://localhost:8090")
    
    httpx_mock.add_response(
        url="http://localhost:8090/api/collections/users/records/user_123/external-auths/github",
        method="DELETE",
        status_code=204
    )

    success = client.collection("users").unlink_external_auth("user_123", "github")
    assert success is True

def test_truncate_collection(httpx_mock):
    client = PocketBase("http://localhost:8090")
    
    httpx_mock.add_response(
        url="http://localhost:8090/api/collections/temporary_logs/truncate",
        method="DELETE",
        status_code=204
    )

    success = client.collections.truncate("temporary_logs")
    assert success is True

def test_get_scaffolds(httpx_mock):
    client = PocketBase("http://localhost:8090")
    
    httpx_mock.add_response(
        url="http://localhost:8090/api/collections/meta/scaffolds",
        method="GET",
        json=[{"type": "base", "name": "new_collection"}, {"type": "auth", "name": "new_users"}]
    )

    scaffolds = client.collections.get_scaffolds()
    
    assert len(scaffolds) == 2
    assert scaffolds[0]["type"] == "base"
    assert scaffolds[1]["type"] == "auth"


def test_collection_create_translates_legacy_schema(httpx_mock):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/collections",
        method="POST",
        json={
            "id": "col_123",
            "name": "demo",
            "type": "base",
            "fields": [
                {"id": "f1", "name": "title", "type": "text", "required": True}
            ],
        },
    )

    client.collections.create(
        {
            "name": "demo",
            "type": "base",
            "schema": [
                {
                    "name": "title",
                    "type": "text",
                    "required": True,
                    "options": {"min": 3},
                }
            ],
        }
    )

    request = httpx_mock.get_request()
    assert request is not None
    body = json.loads(request.content)
    assert "schema" not in body
    assert body["fields"][0]["min"] == 3
