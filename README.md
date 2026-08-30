# hush-hush-python

[![ci](https://github.com/alrayyes/hush-hush-python/actions/workflows/ci.yml/badge.svg)](https://github.com/alrayyes/hush-hush-python/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/alrayyes/hush-hush-python/graph/badge.svg)](https://codecov.io/gh/alrayyes/hush-hush-python)
[![PyPI](https://img.shields.io/pypi/v/hush-hush)](https://pypi.org/project/hush-hush/)
[![release](https://img.shields.io/github/v/release/alrayyes/hush-hush-python)](https://github.com/alrayyes/hush-hush-python/releases)
[![license](https://img.shields.io/github/license/alrayyes/hush-hush-python)](LICENSE)

The official Python SDK for [hush-hush](https://github.com/alrayyes/hush-hush),
generated from its OpenAPI spec and kept in sync with it automatically.

## Install

```sh
pip install hush-hush
```

Requires Python 3.11 or newer.

## Quickstart

```python
from hush_hush import Client

client = Client("https://hush-hush.example.com", api_key="your-api-key")  # or set HUSH_HUSH_API_KEY

# Create is a write operation — it needs the credential above.
client.create_object("my-first-secret", b"already-sealed-ciphertext")

# Get needs no credential — hush-hush's confidentiality boundary is
# "who holds a matching private key," not who's calling this endpoint.
value = client.get_object("my-first-secret")
print(f"got {len(value)} bytes of sealed ciphertext")

# The audit log records every read and write; querying it needs no
# credential either, and returns the full matching result set (there's
# no pagination on this endpoint).
for entry in client.query_audit_log():
    print(entry.action, entry.object_id, entry.timestamp)
```

An `AsyncClient` with the same methods (`await client.get_object(...)`) is
available for async code. The API key is only required for write operations
(create/update/delete); reads (get, used-by, audit-log query) work without
one. `caller`, accepted by most methods, is optional. See the
[full API reference](https://alrayyes.github.io/hush-hush-python/) for
everything else.

## Versioning

This SDK's version tracks hush-hush's OpenAPI spec, not this repo's own
commit history — see [CONTRIBUTING.md](CONTRIBUTING.md) for how a spec
change becomes a release.

## License

[MIT](LICENSE)
