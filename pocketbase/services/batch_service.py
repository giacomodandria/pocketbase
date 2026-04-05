from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from pocketbase.services.utils.base_service import BaseService

if TYPE_CHECKING:
    from pocketbase.client import Client


class BatchCollectionHelper:
    """Helper class to easily queue operations for a specific collection within a batch."""
    def __init__(self, batch_request: BatchRequest, collection_id_or_name: str) -> None:
        self.batch = batch_request
        self.collection = collection_id_or_name
        self.base_url = f"/api/collections/{quote(collection_id_or_name)}/records"

    def create(self, body_params: dict[str, Any] | None = None) -> BatchCollectionHelper:
        self.batch.requests.append({
            "method": "POST",
            "url": self.base_url,
            "body": body_params or {}
        })
        return self

    def update(self, id: str, body_params: dict[str, Any] | None = None) -> BatchCollectionHelper:
        self.batch.requests.append({
            "method": "PATCH",
            "url": f"{self.base_url}/{quote(id)}",
            "body": body_params or {}
        })
        return self

    def upsert(self, body_params: dict[str, Any] | None = None) -> BatchCollectionHelper:
        self.batch.requests.append({
            "method": "PUT",
            "url": self.base_url,
            "body": body_params or {}
        })
        return self

    def delete(self, id: str) -> BatchCollectionHelper:
        self.batch.requests.append({
            "method": "DELETE",
            "url": f"{self.base_url}/{quote(id)}"
        })
        return self


class BatchRequest:
    """Represents a single transactional batch request."""
    def __init__(self, client: Client) -> None:
        self.client = client
        self.requests: list[dict[str, Any]] = []

    def collection(self, collection_id_or_name: str) -> BatchCollectionHelper:
        """Returns a helper to queue operations for a specific collection."""
        return BatchCollectionHelper(self, collection_id_or_name)

    def send(self, query_params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Executes the batch transaction."""
        return self.client.send(
            "/api/batch",
            {
                "method": "POST",
                "body": {"requests": self.requests},
                "params": query_params or {},
            },
        )


class BatchService(BaseService):
    """Factory service for creating batch transactions."""
    
    def create(self) -> BatchRequest:
        """Initializes a new batch transaction request."""
        return BatchRequest(self.client)