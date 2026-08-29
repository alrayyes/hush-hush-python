import pytest

from hush_hush import APIError, Client


def test_typed_error_mapping(make_server):
    def handler(req):
        req.send_json(404, b'{"error":"unknown object"}', headers={"X-Request-Id": "req-123"})

    server = make_server(handler)
    client = Client(server.base_url, max_retries=0)
    with pytest.raises(APIError) as exc_info:
        client.get_object("missing")
    err = exc_info.value
    assert err.status_code == 404
    assert err.message == "unknown object"
    assert err.request_id == "req-123"


def test_typed_error_mapping_no_request_id_header(make_server):
    def handler(req):
        req.send_json(404, b'{"error":"unknown object"}')

    server = make_server(handler)
    client = Client(server.base_url, max_retries=0)
    with pytest.raises(APIError) as exc_info:
        client.get_object("missing")
    assert exc_info.value.request_id is None
