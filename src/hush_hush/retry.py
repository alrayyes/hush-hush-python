"""Retry transports: network failure or an HTTP 5xx/429 response is retried
with exponential backoff and jitter, honoring a Retry-After header ahead of
the computed backoff delay when present. Any other 4xx is never retried —
it won't succeed on a second attempt, and retrying only delays the real
error reaching the caller.
"""

from __future__ import annotations

import email.utils
import random
import time
from datetime import UTC, datetime

import httpx

DEFAULT_MAX_RETRIES = 3


def _is_retryable_status(status_code: int) -> bool:
    return status_code >= 500 or status_code == 429


def _retry_after_seconds(response: httpx.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if not value:
        return None
    try:
        seconds = int(value)
        return float(seconds) if seconds >= 0 else None
    except ValueError:
        pass
    try:
        when = email.utils.parsedate_to_datetime(value)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        delta = (when - datetime.now(UTC)).total_seconds()
        return max(delta, 0.0)
    except (TypeError, ValueError):
        return None


def _backoff_seconds(attempt: int, response: httpx.Response | None) -> float:
    if response is not None:
        retry_after = _retry_after_seconds(response)
        if retry_after is not None:
            return retry_after
    base = 0.1 * (2 ** (attempt - 1))
    return base + random.uniform(0, base)


class RetryTransport(httpx.BaseTransport):
    """Wraps a sync transport with hush-hush's retry policy."""

    def __init__(
        self, transport: httpx.BaseTransport, max_retries: int = DEFAULT_MAX_RETRIES
    ) -> None:
        self._transport = transport
        self._max_retries = max_retries

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        last_response: httpx.Response | None = None
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            if attempt > 0:
                time.sleep(_backoff_seconds(attempt, last_response))
            try:
                response = self._transport.handle_request(request)
            except httpx.TransportError as exc:
                last_error, last_response = exc, None
                continue
            if not _is_retryable_status(response.status_code) or attempt == self._max_retries:
                return response
            response.close()
            last_response, last_error = response, None

        if last_error is not None:
            raise last_error
        assert last_response is not None
        return last_response

    def close(self) -> None:
        self._transport.close()


class AsyncRetryTransport(httpx.AsyncBaseTransport):
    """Wraps an async transport with hush-hush's retry policy."""

    def __init__(
        self, transport: httpx.AsyncBaseTransport, max_retries: int = DEFAULT_MAX_RETRIES
    ) -> None:
        self._transport = transport
        self._max_retries = max_retries

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        import asyncio

        last_response: httpx.Response | None = None
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            if attempt > 0:
                await asyncio.sleep(_backoff_seconds(attempt, last_response))
            try:
                response = await self._transport.handle_async_request(request)
            except httpx.TransportError as exc:
                last_error, last_response = exc, None
                continue
            if not _is_retryable_status(response.status_code) or attempt == self._max_retries:
                return response
            await response.aclose()
            last_response, last_error = response, None

        if last_error is not None:
            raise last_error
        assert last_response is not None
        return last_response

    async def aclose(self) -> None:
        await self._transport.aclose()
