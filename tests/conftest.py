"""A real local HTTP server for tests — the Python analogue of Go's
httptest.Server. Exercises the client against real sockets rather than
mocking httpx internals, so retry/timeout/transport behavior is tested
for real.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

Handler = Callable[["RecordingHTTPRequestHandler"], None]


class RecordingHTTPRequestHandler(BaseHTTPRequestHandler):
    handler_fn: Handler

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass

    def _dispatch(self) -> None:
        self.handler_fn(self)

    do_GET = _dispatch
    do_POST = _dispatch
    do_PUT = _dispatch
    do_DELETE = _dispatch

    def send_json(self, status: int, body: bytes, headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, status: int, body: bytes, headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/octet-stream")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""


class TestServer:
    def __init__(self, handler: Handler) -> None:
        # staticmethod, not a bare function: a plain function stored as a
        # class attribute is a descriptor and binds itself to the instance
        # on access, so self.handler_fn(self) would call handler(self, self).
        RecordingHTTPRequestHandler.handler_fn = staticmethod(handler)
        self._httpd = HTTPServer(("127.0.0.1", 0), RecordingHTTPRequestHandler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    @property
    def base_url(self) -> str:
        host, port = self._httpd.server_address[:2]
        return f"http://{host}:{port}"

    def close(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        self._thread.join(timeout=5)


@pytest.fixture
def make_server() -> Iterator[Callable[[Handler], TestServer]]:
    servers: list[TestServer] = []

    def factory(handler: Handler) -> TestServer:
        server = TestServer(handler)
        servers.append(server)
        return server

    yield factory

    for server in servers:
        server.close()
