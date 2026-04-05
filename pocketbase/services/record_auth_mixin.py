from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from pocketbase.models.external_auth import ExternalAuth
from pocketbase.models.record import Record
from pocketbase.utils import camel_to_snake, validate_token

if TYPE_CHECKING:
    from pocketbase.client import Client


class RecordAuthResponse:
    def __init__(
        self,
        token: str,
        record: Record,
        meta: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self.token = token
        self.record = record
        self.meta = meta
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def is_valid(self) -> bool:
        return validate_token(self.token)


@dataclass
class AuthProviderInfo:
    name: str
    display_name: str
    state: str
    auth_url: str
    code_verifier: str
    code_challenge: str
    code_challenge_method: str


@dataclass
class AuthMethodsList:
    username_password: bool
    email_password: bool
    auth_providers: list[AuthProviderInfo]
    only_verified: bool = False


class RecordAuthMixin:
    """Mixin providing auth-related methods for RecordService."""

    client: Client

    def base_collection_path(self) -> str: ...

    def decode(self, data: dict[str, Any]) -> Record: ...

    def auth_response(
        self, response_data: dict[str, Any]
    ) -> RecordAuthResponse:
        """Prepare successful collection authorization response."""
        record = self.decode(response_data.pop("record", {}))
        token = response_data.pop("token", "")
        if token and record:
            self.client.auth_store.save(token, record)
        return RecordAuthResponse(token=token, record=record, **response_data)  # type: ignore

    def list_auth_methods(
        self, query_params: dict[str, Any] | None = None
    ) -> AuthMethodsList:
        """Returns all available collection auth methods."""
        response_data = self.client.send(
            self.base_collection_path() + "/auth-methods",
            {"method": "GET", "params": query_params},
        )
        username_password = response_data.pop("usernamePassword", False)
        email_password = response_data.pop("emailPassword", False)

        def apply_pythonic_keys(ap: dict[str, Any]) -> dict[str, Any]:
            return {
                camel_to_snake(
                    key, getattr(self.client, "auto_snake_case", True)
                ).replace("@", ""): value
                for key, value in ap.items()
            }

        auth_providers = [
            AuthProviderInfo(**auth_provider)
            for auth_provider in map(
                apply_pythonic_keys,
                response_data.get("authProviders")
                or response_data.get("auth_providers")
                or [],
            )
        ]
        return AuthMethodsList(
            username_password=username_password,
            email_password=email_password,
            auth_providers=auth_providers,
        )

    def auth_with_password(
        self,
        username_or_email: str,
        password: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> RecordAuthResponse:
        """
        Authenticate a single auth collection record via its username/email and password.

        On success, this method also automatically updates
        the client's AuthStore data and returns:
        - the authentication token
        - the authenticated record model
        """
        body_params = body_params or {}
        body_params.update(
            {"identity": username_or_email, "password": password}
        )
        response_data = self.client.send(
            self.base_collection_path() + "/auth-with-password",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
                "headers": {"Authorization": ""},
            },
        )
        return self.auth_response(response_data)

    def auth_with_oauth2(
        self,
        provider: str,
        code: str,
        code_verifier: str,
        redirect_url: str,
        create_data: dict[str, Any] | None = None,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> RecordAuthResponse:
        """
        Authenticate a single auth collection record with OAuth2.

        On success, this method also automatically updates
        the client's AuthStore data and returns:
        - the authentication token
        - the authenticated record model
        - the OAuth2 account data (eg. name, email, avatar, etc.)
        """
        body_params = body_params or {}
        body_params.update(
            {
                "provider": provider,
                "code": code,
                "codeVerifier": code_verifier,
                "redirectUrl": redirect_url,
                "createData": create_data,
            }
        )
        response_data = self.client.send(
            self.base_collection_path() + "/auth-with-oauth2",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return self.auth_response(response_data)

    def auth_refresh(
        self,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> RecordAuthResponse:
        """
        Refreshes the current authenticated record instance and
        returns a new token and record data.

        On success this method also automatically updates the client's AuthStore.
        """
        return self.auth_response(
            self.client.send(
                self.base_collection_path() + "/auth-refresh",
                {"method": "POST", "params": query_params, "body": body_params},
            )
        )

    def request_email_change(
        self,
        newEmail: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Asks to change email of the current authenticated record instance the new address
        receives an email with a confirmation token that needs to be confirmed with confirmEmailChange()
        """
        body_params = body_params or {}
        body_params.update({"newEmail": newEmail})
        self.client.send(
            self.base_collection_path() + "/request-email-change",
            {"method": "POST", "params": query_params, "body": body_params},
        )
        return True

    def confirm_email_change(
        self,
        token: str,
        password: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Confirms Email Change by with the confirmation token and confirm with users password
        """
        body_params = body_params or {}
        body_params.update({"token": token, "password": password})
        self.client.send(
            self.base_collection_path() + "/confirm-email-change",
            {"method": "POST", "params": query_params, "body": body_params},
        )
        return True

    def request_password_reset(
        self,
        email: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """Sends auth record password reset request."""
        body_params = body_params or {}
        body_params.update({"email": email})
        self.client.send(
            self.base_collection_path() + "/request-password-reset",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True

    def request_verification(
        self,
        email: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """Sends email verification request."""
        body_params = body_params or {}
        body_params.update({"email": email})
        self.client.send(
            self.base_collection_path() + "/request-verification",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True

    def confirm_password_reset(
        self,
        password_reset_token: str,
        password: str,
        password_confirm: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """Confirms auth record password reset request"""
        body_params = body_params or {}
        body_params.update(
            {
                "token": password_reset_token,
                "password": password,
                "passwordConfirm": password_confirm,
            }
        )

        self.client.send(
            self.base_collection_path() + "/confirm-password-reset",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return True

    def confirm_verification(
        self,
        token: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """Confirms email verification request."""
        body_params = body_params or {}
        body_params.update({"token": token})
        self.client.send(
            self.base_collection_path() + "/confirm-verification",
            {"method": "POST", "params": query_params, "body": body_params},
        )
        return True

    def request_otp(
        self,
        email: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Sends an email with a One-Time Password and returns the created OTP id.
        """
        body_params = body_params or {}
        body_params.update({"email": email})
        return self.client.send(
            self.base_collection_path() + "/request-otp",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )

    def auth_with_otp(
        self,
        otp_id: str,
        password: str,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> RecordAuthResponse:
        """
        Authenticate a record with an OTP id and the emailed code.
        """
        body_params = body_params or {}
        body_params.update({"otpId": otp_id, "password": password})
        response_data = self.client.send(
            self.base_collection_path() + "/auth-with-otp",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
                "headers": {"Authorization": ""},
            },
        )
        return self.auth_response(response_data)

    def impersonate(
        self,
        id: str,
        duration: int = 0,
        body_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> RecordAuthResponse:
        """
        Generates an auth token for another auth record.
        """
        body_params = body_params or {}
        if duration > 0:
            body_params.update({"duration": duration})

        response_data = self.client.send(
            f"{self.base_collection_path()}/impersonate/{quote(id)}",
            {
                "method": "POST",
                "params": query_params,
                "body": body_params,
            },
        )
        return self.auth_response(response_data)

    def list_external_auths(
        self,
        record_id: str,
        query_params: dict[str, Any] | None = None,
    ) -> list[ExternalAuth]:
        """
        Lists the linked external auth providers for a record.
        """
        response_data = self.client.send(
            f"{self.base_collection_path()}/records/{quote(record_id)}/external-auths",
            {
                "method": "GET",
                "params": query_params,
            },
        )
        return [ExternalAuth(item) for item in response_data]

    def unlink_external_auth(
        self,
        record_id: str,
        provider: str,
        query_params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Unlinks a specific OAuth2 provider from the specified record.
        """
        self.client.send(
            f"{self.base_collection_path()}/records/{quote(record_id)}/external-auths/{quote(provider)}",
            {
                "method": "DELETE",
                "params": query_params,
            },
        )
        return True
