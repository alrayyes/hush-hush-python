"""Records this SDK's real interactions as a Pact consumer contract.
Provider verification against hush-hush's actual server has to run in
hush-hush's own CI (see design.md's Risks — an external dependency this
repo can't wire up unilaterally); this module's job is only to keep
producing an up-to-date pact file for that to consume.
"""

import pytest

from hush_hush import Client
from pact import Pact, match

pytestmark = pytest.mark.pact


def test_get_object():
    pact = Pact("hush-hush-python", "hush-hush")
    (
        pact.upon_receiving("a request to get an object")
        .given("an object exists with id my-object")
        .with_request("GET", "/objects/my-object")
        .will_respond_with(200)
        .with_binary_body(b"sealed-bytes", content_type="application/octet-stream")
    )
    with pact.serve() as srv:
        client = Client(str(srv.url))
        got = client.get_object("my-object")
        assert got == b"sealed-bytes"
    pact.write_file("pact/pacts", overwrite=True)


def test_query_audit_log():
    pact = Pact("hush-hush-python", "hush-hush")
    (
        pact.upon_receiving("a request to query the audit log")
        .given("the audit log has at least one entry")
        .with_request("GET", "/audit-log")
        .will_respond_with(200)
        .with_body(
            match.each_like(
                {
                    "object_id": match.like("my-object"),
                    "action": match.regex("read", regex="create|read|update|delete"),
                    "timestamp": match.timestamp(),
                },
                min=1,
            ),
            content_type="application/json",
        )
    )
    with pact.serve() as srv:
        client = Client(str(srv.url))
        entries = client.query_audit_log()
        assert len(entries) >= 1
    pact.write_file("pact/pacts", overwrite=True)
