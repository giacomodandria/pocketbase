from __future__ import annotations

from typing import Any

from pocketbase.models.utils.base_model import BaseModel
from pocketbase.utils import camel_to_snake


class Record(BaseModel):
    collection_id: str
    collection_name: str
    expand: dict[str, Any]

    def __init__(self, data: dict[str, Any] = {}, client: Any = None) -> None:
        self.client = client
        super().__init__(data)

    def load(self, data: dict[str, Any]) -> None:
        super().load(data)
        self.collection_id = data.get("collectionId", data.get("collection_id", ""))
        self.collection_name = data.get(
            "collectionName", data.get("collection_name", "")
        )
        raw_expand = data.get("expand", {}) or {}
        self.expand = {}
        for key, value in data.items():
            key = camel_to_snake(
                key,
                getattr(self, "client", None)
                and getattr(self.client, "auto_snake_case", True),
            ).replace("@", "")
            setattr(self, key, value)
        self.expand = {
            camel_to_snake(
                key,
                getattr(self, "client", None)
                and getattr(self.client, "auto_snake_case", True),
            ).replace("@", ""): value
            for key, value in raw_expand.items()
        }
        self.load_expanded()

    def parse_expanded(self, data: Any):
        if isinstance(data, list):
            return [
                self.__class__(item, client=getattr(self, "client", None))
                for item in data
            ]
        return self.__class__(data, client=getattr(self, "client", None))

    def load_expanded(self) -> None:
        for key, value in self.expand.items():
            self.expand[key] = self.parse_expanded(value)
