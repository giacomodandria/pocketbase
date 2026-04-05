from pytest_httpx import HTTPXMock

from pocketbase import PocketBase
from pocketbase.services.cron_service import CronJob


def test_get_full_list(httpx_mock: HTTPXMock):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/crons",
        method="GET",
        json=[
            {"id": "db_cleanup", "expression": "0 0 * * *"},
            {"id": "send_digest", "expression": "0 8 * * 1"},
        ],
    )

    result = client.crons.get_full_list()

    assert len(result) == 2
    assert isinstance(result[0], CronJob)
    assert result[0].id == "db_cleanup"
    assert result[0].expression == "0 0 * * *"
    assert result[1].id == "send_digest"
    assert result[1].expression == "0 8 * * 1"


def test_get_full_list_empty(httpx_mock: HTTPXMock):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/crons",
        method="GET",
        json=[],
    )

    result = client.crons.get_full_list()

    assert result == []


def test_run(httpx_mock: HTTPXMock):
    client = PocketBase("http://localhost:8090")

    httpx_mock.add_response(
        url="http://localhost:8090/api/crons/db_cleanup",
        method="POST",
        status_code=204,
        json=None,
    )

    result = client.crons.run("db_cleanup")

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"
    assert request.url.path == "/api/crons/db_cleanup"
    assert result is None
