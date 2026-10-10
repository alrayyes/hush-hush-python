#!/usr/bin/env sh
# Style: house voice, weasel words, corporate speak, the cliches proselint
# knows. Advice, not a gate - Vale only fails on error-severity alerts
# (MinAlertLevel in .vale.ini), which is why this script's own exit code is
# the real signal and nothing here downgrades it.
set -eu

# The official image, pinned by tag and digest so a moved tag can't change the run
# unnoticed. The comment is what Renovate reads to bump both together.
IMAGE=jdkato/vale:v3.17.1@sha256:7dba3c9104ba366f172d119022c4ec53a005f7d14dc1b80e285421a3f0b71657 # renovate: datasource=docker depName=jdkato/vale

cd "$(dirname "$0")/.."

# Given files, lint exactly those and never sync: that is the pre-commit path,
# which judges only what the commit contains and must not touch the network
# (rules/linting.md). The style packages are fetched by a bare run, which is
# what pre-push and CI do; run it once on a fresh clone. With no arguments,
# sync and lint the whole documented set.
if [ "$#" -eq 0 ]; then
  set -- README.md CONTRIBUTING.md CLAUDE.md SECURITY.md
  sync=1
else
  sync=0
fi

if command -v vale >/dev/null 2>&1; then
  [ "$sync" -eq 1 ] && vale sync
  vale "$@"
else
  docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" -w /work \
    -e SYNC="$sync" --entrypoint sh "$IMAGE" \
    -c '[ "$SYNC" -eq 1 ] && vale sync; exec vale "$@"' sh "$@"
fi
