import json
from urllib.parse import parse_qs

from hush_hush import Client


def test_query_audit_log_filters(make_server):
    got_query = {}

    def handler(req):
        got_query["value"] = req.path.split("?", 1)[1] if "?" in req.path else ""
        entries = [
            {
                "id": 1,
                "object_id": "obj-1",
                "action": "read",
                "timestamp": "1970-01-01T00:00:00Z",
                "ip": "203.0.113.1",
            }
        ]
        req.send_json(200, json.dumps(entries).encode())

    server = make_server(handler)
    client = Client(server.base_url)
    entries = client.query_audit_log(object_id="obj-1")
    assert len(entries) == 1
    assert entries[0].object_id == "obj-1"
    # query_audit_log() doesn't expose limit, so the generated client always
    # sends its default (50) alongside whatever filter was actually passed.
    assert parse_qs(got_query["value"]) == {"object_id": ["obj-1"], "limit": ["50"]}


def test_query_audit_log_returns_full_result_set_no_iterator(make_server):
    # hush-hush's /audit-log has no pagination parameters — this is a
    # regression guard against ever reintroducing a cursor/iterator, not a
    # test of real pagination behavior.
    def handler(req):
        entries = [
            {
                "id": i,
                "object_id": "obj",
                "action": "read",
                "timestamp": "1970-01-01T00:00:00Z",
                "ip": "203.0.113.1",
            }
            for i in range(250)
        ]
        req.send_json(200, json.dumps(entries).encode())

    server = make_server(handler)
    client = Client(server.base_url)
    entries = client.query_audit_log()
    assert len(entries) == 250
