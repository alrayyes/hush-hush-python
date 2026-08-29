"""Runs the client against a Prism mock server generated from hush-hush's
own pinned spec (see .github/workflows/ci.yml's "contract" job) — never a
hand-rolled stub. See design.md's testing layers: this proves the client's
requests/responses conform to the spec; it says nothing about whether the
real server still matches that spec, which is what the Pact consumer
contract in ../pact is for.
"""

import os

import pytest

from hush_hush import Client

pytestmark = pytest.mark.contract


@pytest.fixture
def client():
    base_url = os.environ.get("HUSH_HUSH_BASE_URL")
    if not base_url:
        pytest.fail(
            "HUSH_HUSH_BASE_URL must point at a running Prism mock (see ci.yml's contract job)"
        )
    return Client(base_url, api_key="prism-does-not-check-this")


def test_health(client):
    client.health()


def test_create_get_delete_object(client):
    client.create_object(
        "contract-test-object", b"sealed-value", caller="hush-hush-python-contract-test"
    )
    client.get_object("contract-test-object")
    client.delete_object("contract-test-object")


def test_query_audit_log(client):
    client.query_audit_log()
