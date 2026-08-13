#!/usr/bin/env python3
"""Sign a package manifest for promotion into striahub-registry.

Writes package.sig next to the manifest: base64 (standard alphabet, no
line wraps) of the detached Ed25519 signature over the manifest file's
exact bytes. Matches the venturi verifier construction in
venturi-rs/crates/venturi-runtime/src/trust.rs (`verify()`, step 6):
base64::engine::general_purpose::STANDARD, ed25519_dalek Signature over
the raw manifest bytes, no re-encoding or normalization of the manifest
in between.

Usage:
    scripts/sign-package.py <manifest.json> <publisher-private-key.pem> [out.sig]

publisher-private-key.pem is a PKCS#8 PEM Ed25519 private key, e.g.
testkeys/test-publisher/key.private.pem for the TEST-ONLY seed publisher.
"""
import base64
import os
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def sign(manifest_path: str, private_key_path: str, out_path: str) -> str:
    manifest_bytes = open(manifest_path, "rb").read()
    key_pem = open(private_key_path, "rb").read()
    private_key = serialization.load_pem_private_key(key_pem, password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise SystemExit(f"{private_key_path} is not an Ed25519 private key")
    signature = private_key.sign(manifest_bytes)
    encoded = base64.b64encode(signature).decode("ascii")
    with open(out_path, "w") as f:
        f.write(encoded)
    return encoded


def main() -> None:
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    manifest_path, private_key_path = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) == 4 else os.path.join(os.path.dirname(manifest_path), "package.sig")
    encoded = sign(manifest_path, private_key_path, out_path)
    print(f"wrote {out_path} ({len(encoded)} b64 chars)")


if __name__ == "__main__":
    main()
