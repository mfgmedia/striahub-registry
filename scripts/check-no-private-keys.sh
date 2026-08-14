#!/usr/bin/env bash
# Fail the repo if any private key material lands under publishers/.
#
# publishers/<slug>/ is the production trust-anchor namespace (only key.pem +
# claim.json belong there — see README.md "Publishers"). Private keys,
# including TEST-ONLY fixtures, live under testkeys/<slug>/ instead.
#
# Run: scripts/check-no-private-keys.sh
set -euo pipefail

cd "$(dirname "$0")/.."

if grep -rlE 'BEGIN.*PRIVATE KEY' publishers/ 2>/dev/null; then
    echo "error: private key material found under publishers/ (see above)." >&2
    echo "Private keys belong under testkeys/<slug>/, never publishers/<slug>/." >&2
    exit 1
fi

echo "OK: no private key material under publishers/"
