import pytest

from pocketbase import PocketBase
from pocketbase.errors import ClientResponseError
from pocketbase.services.cron_service import CronJob


class TestCronService:
    def test_get_full_list(self, client: PocketBase, state):
        ret = client.crons.get_full_list()
        assert isinstance(ret, list)
        for item in ret:
            assert isinstance(item, CronJob)
            assert isinstance(item.id, str)
            assert isinstance(item.expression, str)
        state.crons = ret

    def test_run(self, client: PocketBase, state):
        if not state.crons:
            pytest.skip("no cron jobs available to trigger")
        client.crons.run(state.crons[0].id)

    def test_run_nonexistent(self, client: PocketBase, state):
        with pytest.raises(ClientResponseError):
            client.crons.run("__nonexistent_cron_id__")
