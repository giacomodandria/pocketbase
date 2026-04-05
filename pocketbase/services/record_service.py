from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import quote, urlencode

from pocketbase.models.record import Record
from pocketbase.services.realtime_service import Callable, MessageData
from pocketbase.services.record_auth_mixin import (
    AuthMethodsList,
    AuthProviderInfo,
    RecordAuthMixin,
    RecordAuthResponse,
)
from pocketbase.services.utils.crud_service import CrudService
from pocketbase.utils import deprecated

if TYPE_CHECKING:
    from pocketbase.client import Client

# Re-export for backward compatibility
__all__ = [
    "RecordService",
    "RecordAuthResponse",
    "AuthProviderInfo",
    "AuthMethodsList",
]


class RecordService(RecordAuthMixin, CrudService[Record]):
    collection_id_or_name: str

    def __init__(self, client: Client, collection_id_or_name: str) -> None:
        super().__init__(client)
        self.collection_id_or_name = collection_id_or_name

    def decode(self, data: dict[str, Any]) -> Record:
        return Record(data, client=self.client)

    def base_crud_path(self) -> str:
        return self.base_collection_path() + "/records"

    def update(
        self,
        id: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> Record:
        """
        If the current `client.auth_store.model` matches with the updated id, then
        on success the `client.auth_store.model` will be updated with the result.
        """
        item = super().update(
            id, body_params=body_params, query_params=query_params
        )
        model = self.client.auth_store.model
        if not isinstance(model, Record):
            return item
        if model.id == item.id and (
            model.collection_id == self.collection_id_or_name
            or model.collection_name == self.collection_id_or_name
        ):
            self.client.auth_store.save(self.client.auth_store.token, item)
        return item

    def delete(
        self, id: str, query_params: dict[str, Any] | None = None
    ) -> bool:
        """
        If the current `client.auth_store.model` matches with the deleted id,
        then on success the `client.auth_store` will be cleared.
        """
        success = super().delete(id, query_params)
        model = self.client.auth_store.model
        if not isinstance(model, Record):
            return success
        if (
            success
            and model.id == id
            and (
                model.collection_id == self.collection_id_or_name
                or model.collection_name == self.collection_id_or_name
            )
        ):
            self.client.auth_store.clear()
        return success

    def base_collection_path(self) -> str:
        """Returns the current collection service base path."""
        return "/api/collections/" + quote(self.collection_id_or_name)

    # ----------------
    # Realtime methods
    # ----------------

    def subscribe(self, callback: Callable[[MessageData], None]) -> None:
        """Subscribe to realtime changes of any record from the collection."""
        return self.client.realtime.subscribe(
            self.collection_id_or_name, callback
        )

    def unsubscribe(self, *record_ids: str) -> None:
        """Unsubscribe to the realtime changes of a single record in the collection."""
        if record_ids and len(record_ids) > 0:
            subs: list[str] = []
            for id in record_ids:
                subs.append(self.collection_id_or_name + "/" + id)
            return self.client.realtime.unsubscribe(subs)
        return self.client.realtime.unsubscribe_by_prefix(
            self.collection_id_or_name
        )

    # -------------------
    # Deprecated aliases
    # -------------------

    @deprecated("subscribe")
    def subscribeOne(
        self, record_id: str, callback: Callable[[MessageData], None]
    ) -> None:
        """Subscribe to the realtime changes of a single record in the collection."""
        return self.client.realtime.subscribe(
            self.collection_id_or_name + "/" + record_id, callback
        )

    @deprecated("client.files.get_url")
    def get_file_url(
        self, record: Record, filename: str, query_params: dict[str, Any] = {}
    ) -> str:
        """Builds and returns an absolute record file url."""
        base_url = self.client.base_url
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        result = f"{base_url}/api/files/{record.collection_id}/{record.id}/{filename}"
        if query_params:
            result += "?" + urlencode(query_params)
        return result

    @deprecated("auth_refresh")
    def authRefresh(
        self,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> RecordAuthResponse:
        return self.auth_refresh(body_params, query_params)

    @deprecated("request_email_change")
    def requestEmailChange(
        self,
        newEmail: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        return self.request_email_change(newEmail, body_params, query_params)

    @deprecated("confirm_email_change")
    def confirmEmailChange(
        self,
        token: str,
        password: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        return self.confirm_email_change(
            token, password, body_params, query_params
        )

    @deprecated("request_password_reset")
    def requestPasswordReset(
        self,
        email: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        return self.request_password_reset(email, body_params, query_params)

    @deprecated("request_verification")
    def requestVerification(
        self,
        email: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        return self.request_verification(email, body_params, query_params)

    @deprecated("confirm_password_reset")
    def confirmPasswordReset(
        self,
        password_reset_token: str,
        password: str,
        password_confirm: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        return self.confirm_password_reset(
            password_reset_token,
            password,
            password_confirm,
            body_params,
            query_params,
        )

    @deprecated("confirm_verification")
    def confirmVerification(
        self,
        token: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        return self.confirm_verification(token, body_params, query_params)
