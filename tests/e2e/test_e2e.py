"""The thin, deliberately sparse layer against a real staging hush-hush
instance — see design.md's testing layers and .github/workflows/e2e.yml,
which gates this to release/nightly, never the default PR pipeline.
"""

import os
import uuid

import pytest

from hush_hush import Client

pytestmark = pytest.mark.e2e


def test_smoke_create_get_delete_round_trip():
    base_url = os.environ.get("HUSH_HUSH_BASE_URL")
    api_key = os.environ.get("HUSH_HUSH_API_KEY")
    if not base_url or not api_key:
        pytest.skip("HUSH_HUSH_BASE_URL and HUSH_HUSH_API_KEY must be set to run against staging")

    client = Client(base_url, api_key=api_key)
    object_id = f"hush-hush-python-e2e-smoke-{uuid.uuid4().hex[:8]}"
    caller = "hush-hush-python-e2e"

    client.create_object(object_id, b"e2e-smoke-value", caller=caller)
    try:
        got = client.get_object(object_id, caller=caller)
        assert got == b"e2e-smoke-value"
    finally:
        client.delete_object(object_id, caller=caller)
