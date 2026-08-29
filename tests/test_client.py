import json

import pytest

from hush_hush import AsyncClient, Client


def test_credential_from_environment(make_server, monkeypatch):
    monkeypatch.setenv("HUSH_HUSH_API_KEY", "env-token")
    got_auth = {}

    def handler(req):
        got_auth["value"] = req.headers.get("Authorization")
        req.send_json(201, json.dumps({"id": "x"}).encode())

    server = make_server(handler)
    client = Client(server.base_url)
    client.create_object("x", b"v")
    assert got_auth["value"] == "Bearer env-token"


def test_explicit_credential_overrides_environment(make_server, monkeypatch):
    monkeypatch.setenv("HUSH_HUSH_API_KEY", "env-token")
    got_auth = {}

    def handler(req):
        got_auth["value"] = req.headers.get("Authorization")
        req.send_json(201, json.dumps({"id": "x"}).encode())

    server = make_server(handler)
    client = Client(server.base_url, api_key="explicit-token")
    client.create_object("x", b"v")
    assert got_auth["value"] == "Bearer explicit-token"


def test_unauthenticated_read_succeeds(make_server, monkeypatch):
    monkeypatch.delenv("HUSH_HUSH_API_KEY", raising=False)
    got_auth = {}

    def handler(req):
        got_auth["value"] = req.headers.get("Authorization")
        req.send_bytes(200, b"sealed-bytes")

    server = make_server(handler)
    client = Client(server.base_url)  # no credential set at all
    got = client.get_object("my-object")
    assert got == b"sealed-bytes"
    assert got_auth["value"] is None


def test_x_caller_is_per_request(make_server):
    got_caller = {}

    def handler(req):
        got_caller["value"] = req.headers.get("X-Caller")
        req.send_bytes(200, b"bytes")

    server = make_server(handler)
    client = Client(server.base_url)

    client.get_object("obj", caller="caller-a")
    assert got_caller["value"] == "caller-a"

    client.get_object("obj")
    assert got_caller["value"] is None


@pytest.mark.asyncio
async def test_async_client_get_object(make_server):
    def handler(req):
        req.send_bytes(200, b"sealed-bytes")

    server = make_server(handler)
    client = AsyncClient(server.base_url)
    got = await client.get_object("obj")
    assert got == b"sealed-bytes"
