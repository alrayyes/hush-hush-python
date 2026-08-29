import time

import pytest

from hush_hush import APIError, Client


def test_retries_503(make_server):
    attempts = {"n": 0}

    def handler(req):
        attempts["n"] += 1
        if attempts["n"] < 3:
            req.send_response(503)
            req.end_headers()
            return
        req.send_bytes(200, b"ok")

    server = make_server(handler)
    client = Client(server.base_url, max_retries=3)
    got = client.get_object("obj")
    assert got == b"ok"
    assert attempts["n"] == 3


def test_retry_after_takes_priority(make_server):
    timestamps = {}

    def handler(req):
        if "first" not in timestamps:
            timestamps["first"] = time.monotonic()
            req.send_response(429)
            req.send_header("Retry-After", "1")
            req.end_headers()
            return
        timestamps["second"] = time.monotonic()
        req.send_bytes(200, b"ok")

    server = make_server(handler)
    client = Client(server.base_url, max_retries=1)
    client.get_object("obj")
    assert timestamps["second"] - timestamps["first"] >= 1.0


def test_does_not_retry_400(make_server):
    attempts = {"n": 0}

    def handler(req):
        attempts["n"] += 1
        req.send_json(400, b'{"error":"bad request"}')

    server = make_server(handler)
    client = Client(server.base_url, max_retries=3)
    with pytest.raises(APIError) as exc_info:
        client.get_object("obj")
    assert exc_info.value.status_code == 400
    assert attempts["n"] == 1
