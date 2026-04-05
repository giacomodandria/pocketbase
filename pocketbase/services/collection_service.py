from __future__ import annotations

from copy import deepcopy
from typing import Any
from urllib.parse import quote

from pocketbase.models.collection import Collection
from pocketbase.services.utils.crud_service import CrudService


class CollectionService(CrudService[Collection]):
    def decode(self, data: dict[str, Any]) -> Collection:
        return Collection(data)

    def _normalize_field(self, field: dict[str, Any]) -> dict[str, Any]:
        normalized = deepcopy(field)
        options = normalized.pop("options", None)
        if isinstance(options, dict):
            for key, value in options.items():
                normalized.setdefault(key, value)
        return normalized

    def _normalize_collection_body(
        self, body_params: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        if body_params is None:
            return None
        normalized = deepcopy(body_params)
        if "schema" in normalized and "fields" not in normalized:
            schema = normalized.pop("schema") or []
            normalized["fields"] = [
                self._normalize_field(field) for field in schema
            ]
        elif "fields" in normalized:
            normalized["fields"] = [
                self._normalize_field(field)
                for field in (normalized["fields"] or [])
            ]
        return normalized

    def base_crud_path(self) -> str:
        return "/api/collections"

    def create(
        self,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> Collection:
        return super().create(
            body_params=self._normalize_collection_body(body_params),
            query_params=query_params,
        )

    def update(
        self,
        id: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> Collection:
        return super().update(
            id,
            body_params=self._normalize_collection_body(body_params),
            query_params=query_params,
        )

    def import_collections(
        self,
        collections: list[dict[str, Any]],
        delete_missing: bool = False,
        query_params: dict[str, Any] = {},
    ) -> bool:
        """
        Imports the provided collections.

        If `delete_missing` is `True`, all local collections and schema fields,
        that are not present in the imported configuration, WILL BE DELETED
        (including their related records data)!
        """
        normalized_collections = [
            self._normalize_collection_body(collection) for collection in collections
        ]
        self.client.send(
            self.base_crud_path() + "/import",
            {
                "method": "PUT",
                "params": query_params,
                "body": {
                    "collections": normalized_collections,
                    "deleteMissing": delete_missing,
                },
            },
        )
        return True

    def truncate(
        self,
        id_or_name: str,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Deletes all records associated with a collection without removing it.
        """
        self.client.send(
            f"{self.base_crud_path()}/{quote(id_or_name)}/truncate",
            {
                "method": "DELETE",
                "params": query_params,
            },
        )
        return True

    def get_scaffolds(
        self,
        query_params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Returns the scaffolded collection models exposed by the API.
        """
        return self.client.send(
            self.base_crud_path() + "/meta/scaffolds",
            {
                "method": "GET",
                "params": query_params,
            },
        )
