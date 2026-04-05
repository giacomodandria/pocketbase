import pytest
import os

from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError


class State:
    def __init__(self):
        pass


def require_tmp_email_dir() -> str:
    mail_dir = os.getenv("TMP_EMAIL_DIR", "")
    if not mail_dir:
        pytest.skip(
            "TMP_EMAIL_DIR is not set. Email integration tests require the "
            "disposable sendmail setup from tests/integration/pocketbase."
        )
    if not os.path.isdir(mail_dir):
        pytest.skip(
            f"TMP_EMAIL_DIR points to a missing directory: {mail_dir!r}"
        )
    return mail_dir


@pytest.fixture(scope="class")
def state() -> State:
    return State()


@pytest.fixture(scope="class")
def client() -> PocketBase:
    url = os.getenv("POCKETBASE_URL", "http://127.0.0.1:8090")
    has_test_email = "POCKETBASE_TEST_EMAIL" in os.environ
    has_test_password = "POCKETBASE_TEST_PASSWORD" in os.environ
    email = os.getenv(
        "POCKETBASE_TEST_EMAIL", "68e82c0b58bd4ac0@8e8b3687496517e7.com"
    )
    password = os.getenv(
        "POCKETBASE_TEST_PASSWORD", "2f199a97ac9e42e3b9e59b9d939b6e5f"
    )
    client = PocketBase(url)

    try:
        client.health.check()
    except Exception as exc:
        pytest.skip(f"PocketBase not reachable at {url}: {exc}")

    try:
        client.admins.auth_with_password(str(email), str(password))
        return client
    except ClientResponseError as exc:
        message = (
            f"PocketBase is reachable at {url}, but superuser auth failed for "
            f"{email!r}. Set POCKETBASE_TEST_EMAIL and POCKETBASE_TEST_PASSWORD "
            "to a valid superuser account, or start the disposable integration "
            "server via tests/integration/pocketbase."
        )
        if has_test_email or has_test_password:
            pytest.fail(f"{message}\nOriginal error:\n{exc}")
        pytest.skip(message)
