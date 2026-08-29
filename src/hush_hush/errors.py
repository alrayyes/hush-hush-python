"""Typed errors raised for any non-2xx response from hush-hush."""

from __future__ import annotations

import json

import httpx


class APIError(Exception):
    """Raised for any non-2xx response from hush-hush.

    Attributes:
        status_code: The HTTP status hush-hush responded with.
        request_id: Populated when the response carries a documented
            request-ID header; hush-hush's spec doesn't currently document
            one, so this is usually ``None``. Kept as an attribute rather
            than omitted so a future spec addition doesn't change this
            type's shape.
        message: The parsed ``error`` field from hush-hush's error body, or
            ``None`` if the body wasn't the expected shape.
        body: The raw, unparsed response body, for a caller that needs more
            than ``message``.
    """

    def __init__(self, response: httpx.Response) -> None:
        self.status_code = response.status_code
        self.request_id: str | None = response.headers.get("X-Request-Id")
        self.body: bytes = response.content
        self.message: str | None = None
        try:
            parsed = json.loads(response.content)
            if isinstance(parsed, dict):
                self.message = parsed.get("error")
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        super().__init__(
            f"hushhush: {self.status_code}: {self.message}"
            if self.message
            else f"hushhush: unexpected status {self.status_code}"
        )
