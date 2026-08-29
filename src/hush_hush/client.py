"""Sync and async hush-hush clients."""

from __future__ import annotations

import base64
import os
from datetime import datetime

import httpx

from ._generated.api.audit_log import query_audit_log as _query_audit_log
from ._generated.api.health import health as _health
from ._generated.api.objects import create_object as _create_object
from ._generated.api.objects import delete_object as _delete_object
from ._generated.api.objects import get_object as _get_object
from ._generated.api.objects import get_object_used_by as _get_object_used_by
from ._generated.api.objects import update_object as _update_object
from ._generated.client import AuthenticatedClient as _AuthenticatedClient
from ._generated.client import Client as _GeneratedClient
from ._generated.models.audit_log_entry import AuditLogEntry
from ._generated.models.create_object_request import CreateObjectRequest as _CreateObjectRequestBody
from ._generated.models.health import Health
from ._generated.models.object_metadata import ObjectMetadata
from ._generated.models.update_object_request import UpdateObjectRequest as _UpdateObjectRequestBody
from ._generated.models.used_by import UsedBy
from ._generated.types import UNSET
from .errors import APIError
from .retry import AsyncRetryTransport, RetryTransport

API_KEY_ENV_VAR = "HUSH_HUSH_API_KEY"
"""Environment variable `Client`/`AsyncClient` fall back to when `api_key`
isn't passed explicitly."""

DEFAULT_TIMEOUT = 30.0
"""Default per-request timeout, in seconds, used when `timeout` isn't
passed explicitly."""

__all__ = [
    "API_KEY_ENV_VAR",
    "APIError",
    "AsyncClient",
    "AuditLogEntry",
    "Client",
    "Health",
    "ObjectMetadata",
    "UsedBy",
]


def _resolve_api_key(api_key: str | None) -> str | None:
    return api_key if api_key is not None else os.environ.get(API_KEY_ENV_VAR)


def _raise_for_status(response: httpx.Response, ok_status: int) -> None:
    """Raises APIError if response's status isn't the one success status
    this operation documents. hush-hush's read paths only ever document one
    success status each, so this doesn't need to handle a set of them.
    """
    if response.status_code != ok_status:
        raise APIError(response)


class Client:
    """Synchronous hush-hush client.

    A single instance handles both read and write calls. The credential is
    only actually required by hush-hush on write operations
    (create/update/delete); reads (get, used-by, audit-log query) succeed
    without one, since hush-hush's confidentiality boundary is "who holds a
    matching private key," not who's calling the endpoint.

    Args:
        base_url: Base URL of the hush-hush instance to call, e.g.
            `"https://hush-hush.example.com"`.
        api_key: Bearer credential for write operations. Falls back to the
            `HUSH_HUSH_API_KEY` environment variable when not given.
        timeout: Per-request timeout, in seconds.
        max_retries: How many times a request is retried after a network
            failure or a 5xx/429 response before the error is raised to the
            caller. Any other 4xx is never retried.
    """

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ) -> None:
        resolved_key = _resolve_api_key(api_key)
        transport = RetryTransport(httpx.HTTPTransport(), max_retries=max_retries)
        httpx_args = {"transport": transport}
        if resolved_key:
            self._client = _AuthenticatedClient(
                base_url=base_url,
                token=resolved_key,
                timeout=httpx.Timeout(timeout),
                httpx_args=httpx_args,
            )
        else:
            self._client = _GeneratedClient(
                base_url=base_url, timeout=httpx.Timeout(timeout), httpx_args=httpx_args
            )

    def health(self) -> Health:
        """Checks whether hush-hush is up. Needs no credential.

        Returns:
            The server's health status.

        Raises:
            APIError: If the server responds with anything other than 200.
        """
        response = _health.sync_detailed(client=self._client)
        _raise_for_status(response, 200)
        assert isinstance(response.parsed, Health)
        return response.parsed

    def create_object(
        self, id: str, value: bytes, *, used_by: list[str] | None = None, caller: str | None = None
    ) -> ObjectMetadata:
        """Stores an already-sealed value under a new object id. Requires a
        credential (see `api_key`/`HUSH_HUSH_API_KEY`).

        Args:
            id: The new object's id. Must match hush-hush's id pattern
                (lowercase alphanumeric, `-`/`_`).
            value: The already-sealed (encrypted) value. This SDK never
                encrypts or decrypts anything — hush-hush stores whatever
                bytes it's given as opaque ciphertext.
            used_by: Consumers (repos or hosts) recorded as depending on
                this object. Set once, at creation; unaffected by later
                value updates.
            caller: Recorded in the audit log as the calling program's
                self-reported identity. Not verified by the server.

        Returns:
            The created object's metadata.

        Raises:
            APIError: If the server responds with anything other than 201
                (for example, 401 for a missing/invalid credential, or 409
                if an object already exists under that id).
        """
        body = _CreateObjectRequestBody(
            id=id, value=base64.b64encode(value).decode("ascii"), used_by=used_by or UNSET
        )
        response = _create_object.sync_detailed(
            client=self._client, body=body, x_caller=caller or UNSET
        )
        _raise_for_status(response, 201)
        assert isinstance(response.parsed, ObjectMetadata)
        return response.parsed

    def get_object(self, id: str, *, caller: str | None = None) -> bytes:
        """Fetches an object's sealed ciphertext exactly as stored — this
        SDK never decrypts it, the same as the server. Needs no credential.

        Args:
            id: The object's id.
            caller: Recorded in the audit log as the calling program's
                self-reported identity. Not verified by the server.

        Returns:
            The object's raw sealed ciphertext.

        Raises:
            APIError: If the server responds with anything other than 200
                (for example, 404 if no object exists under that id).
        """
        response = _get_object.sync_detailed(id=id, client=self._client, x_caller=caller or UNSET)
        _raise_for_status(response, 200)
        return response.content

    def update_object(self, id: str, value: bytes, *, caller: str | None = None) -> ObjectMetadata:
        """Replaces the stored ciphertext for an existing object. The
        object's id and used-by metadata are unchanged. Requires a
        credential.

        Args:
            id: The existing object's id.
            value: The new already-sealed (encrypted) value.
            caller: Recorded in the audit log as the calling program's
                self-reported identity. Not verified by the server.

        Returns:
            The updated object's metadata.

        Raises:
            APIError: If the server responds with anything other than 200
                (for example, 401 or 404).
        """
        body = _UpdateObjectRequestBody(value=base64.b64encode(value).decode("ascii"))
        response = _update_object.sync_detailed(
            id=id, client=self._client, body=body, x_caller=caller or UNSET
        )
        _raise_for_status(response, 200)
        assert isinstance(response.parsed, ObjectMetadata)
        return response.parsed

    def delete_object(self, id: str, *, caller: str | None = None) -> None:
        """Permanently removes an object. A subsequent get by this id
        returns a 404 APIError. Requires a credential.

        Args:
            id: The object's id.
            caller: Recorded in the audit log as the calling program's
                self-reported identity. Not verified by the server.

        Raises:
            APIError: If the server responds with anything other than 204
                (for example, 401 or 404).
        """
        response = _delete_object.sync_detailed(
            id=id, client=self._client, x_caller=caller or UNSET
        )
        _raise_for_status(response, 204)

    def get_object_used_by(self, id: str) -> UsedBy:
        """Returns the recorded list of consumers for an object — the "what
        depends on this" mapping set at creation. Needs no credential.

        Args:
            id: The object's id.

        Returns:
            The object's recorded consumers.

        Raises:
            APIError: If the server responds with anything other than 200
                (for example, 404 if no object exists under that id).
        """
        response = _get_object_used_by.sync_detailed(id=id, client=self._client)
        _raise_for_status(response, 200)
        assert isinstance(response.parsed, UsedBy)
        return response.parsed

    def query_audit_log(
        self,
        *,
        object_id: str | None = None,
        caller: str | None = None,
        from_: datetime | None = None,
        to: datetime | None = None,
    ) -> list[AuditLogEntry]:
        """Queries the audit log — every create, read, update, and delete
        call is recorded here. Needs no credential. Filters combine with
        AND when more than one is given.

        hush-hush's `/audit-log` endpoint has no pagination parameters, so
        this always returns the full matching result set as a single list,
        never a page plus a cursor.

        Args:
            object_id: Restrict to entries for this object id.
            caller: Restrict to entries recorded with this caller identity.
            from_: Restrict to entries at or after this time.
            to: Restrict to entries at or before this time.

        Returns:
            Matching audit log entries, oldest first.

        Raises:
            APIError: If the server responds with anything other than 200.
        """
        response = _query_audit_log.sync_detailed(
            client=self._client,
            object_id=object_id or UNSET,
            caller=caller or UNSET,
            from_=from_ or UNSET,
            to=to or UNSET,
        )
        _raise_for_status(response, 200)
        assert isinstance(response.parsed, list)
        return response.parsed


class AsyncClient:
    """Asynchronous hush-hush client — see [Client][hush_hush.Client] for
    the shared behavior every method here has an `await`-able equivalent of.
    """

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ) -> None:
        resolved_key = _resolve_api_key(api_key)
        transport = AsyncRetryTransport(httpx.AsyncHTTPTransport(), max_retries=max_retries)
        httpx_args = {"transport": transport}
        if resolved_key:
            self._client = _AuthenticatedClient(
                base_url=base_url,
                token=resolved_key,
                timeout=httpx.Timeout(timeout),
                httpx_args=httpx_args,
            )
        else:
            self._client = _GeneratedClient(
                base_url=base_url, timeout=httpx.Timeout(timeout), httpx_args=httpx_args
            )

    async def health(self) -> Health:
        """See [Client.health][hush_hush.Client.health]."""
        response = await _health.asyncio_detailed(client=self._client)
        _raise_for_status(response, 200)
        assert isinstance(response.parsed, Health)
        return response.parsed

    async def create_object(
        self, id: str, value: bytes, *, used_by: list[str] | None = None, caller: str | None = None
    ) -> ObjectMetadata:
        """See [Client.create_object][hush_hush.Client.create_object]."""
        body = _CreateObjectRequestBody(
            id=id, value=base64.b64encode(value).decode("ascii"), used_by=used_by or UNSET
        )
        response = await _create_object.asyncio_detailed(
            client=self._client, body=body, x_caller=caller or UNSET
        )
        _raise_for_status(response, 201)
        assert isinstance(response.parsed, ObjectMetadata)
        return response.parsed

    async def get_object(self, id: str, *, caller: str | None = None) -> bytes:
        """See [Client.get_object][hush_hush.Client.get_object]."""
        response = await _get_object.asyncio_detailed(
            id=id, client=self._client, x_caller=caller or UNSET
        )
        _raise_for_status(response, 200)
        return response.content

    async def update_object(
        self, id: str, value: bytes, *, caller: str | None = None
    ) -> ObjectMetadata:
        """See [Client.update_object][hush_hush.Client.update_object]."""
        body = _UpdateObjectRequestBody(value=base64.b64encode(value).decode("ascii"))
        response = await _update_object.asyncio_detailed(
            id=id, client=self._client, body=body, x_caller=caller or UNSET
        )
        _raise_for_status(response, 200)
        assert isinstance(response.parsed, ObjectMetadata)
        return response.parsed

    async def delete_object(self, id: str, *, caller: str | None = None) -> None:
        """See [Client.delete_object][hush_hush.Client.delete_object]."""
        response = await _delete_object.asyncio_detailed(
            id=id, client=self._client, x_caller=caller or UNSET
        )
        _raise_for_status(response, 204)

    async def get_object_used_by(self, id: str) -> UsedBy:
        """See [Client.get_object_used_by][hush_hush.Client.get_object_used_by]."""
        response = await _get_object_used_by.asyncio_detailed(id=id, client=self._client)
        _raise_for_status(response, 200)
        assert isinstance(response.parsed, UsedBy)
        return response.parsed

    async def query_audit_log(
        self,
        *,
        object_id: str | None = None,
        caller: str | None = None,
        from_: datetime | None = None,
        to: datetime | None = None,
    ) -> list[AuditLogEntry]:
        """See [Client.query_audit_log][hush_hush.Client.query_audit_log]."""
        response = await _query_audit_log.asyncio_detailed(
            client=self._client,
            object_id=object_id or UNSET,
            caller=caller or UNSET,
            from_=from_ or UNSET,
            to=to or UNSET,
        )
        _raise_for_status(response, 200)
        assert isinstance(response.parsed, list)
        return response.parsed
