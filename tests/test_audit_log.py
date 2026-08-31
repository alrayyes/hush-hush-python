import json

from hush_hush import Client


def test_query_audit_log_filters(make_server):
    got_query = {}

    def handler(req):
        got_query["value"] = req.path.split("?", 1)[1] if "?" in req.path else ""
        entries = [
            {
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
    assert got_query["value"] == "object_id=obj-1"


def test_query_audit_log_returns_full_result_set_no_iterator(make_server):
    # hush-hush's /audit-log has no pagination parameters — this is a
    # regression guard against ever reintroducing a cursor/iterator, not a
    # test of real pagination behavior.
    def handler(req):
        entries = [
            {
                "object_id": "obj",
                "action": "read",
                "timestamp": "1970-01-01T00:00:00Z",
                "ip": "203.0.113.1",
            }
            for _ in range(250)
        ]
        req.send_json(200, json.dumps(entries).encode())

    server = make_server(handler)
    client = Client(server.base_url)
    entries = client.query_audit_log()
    assert len(entries) == 250
