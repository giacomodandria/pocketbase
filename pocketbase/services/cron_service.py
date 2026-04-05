from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from pocketbase.services.utils import BaseService


@dataclass
class CronJob:
    id: str
    expression: str

    def __init__(self, data: dict[str, Any]) -> None:
        self.id = data.get("id", "")
        self.expression = data.get("expression", "")


class CronService(BaseService):
    def get_full_list(
        self, query_params: dict[str, Any] | None = None
    ) -> list[CronJob]:
        """Returns a list of all available cron jobs."""
        response_data = self.client.send(
            "/api/crons",
            {"method": "GET", "params": query_params},
        )
        return [CronJob(item) for item in (response_data or [])]

    def run(
        self, job_id: str, query_params: dict[str, Any] | None = None
    ) -> None:
        """Manually triggers the specified cron job."""
        self.client.send(
            "/api/crons/" + quote(job_id),
            {"method": "POST", "params": query_params},
        )
