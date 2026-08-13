#!/usr/bin/env python3
"""Self-check for sign-package.py: sign a manifest with the TEST-ONLY seed
publisher key, verify the signature against its public key, and confirm a
tampered manifest is rejected. Mirrors the exact construction
venturi-rs/crates/venturi-runtime/src/trust.rs verifies against.

Run: python3 scripts/test_sign_package.py
"""
import base64
import os
import subprocess
import sys
import tempfile

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY_ROOT = os.path.dirname(HERE)
PUB_KEY = os.path.join(REGISTRY_ROOT, "publishers", "test-publisher", "key.pem")
PRIV_KEY = os.path.join(REGISTRY_ROOT, "publishers", "test-publisher", "key.private.pem")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = os.path.join(tmp, "package.json")
        with open(manifest_path, "wb") as f:
            f.write(b'{"package_id":"test-publisher.demo","package_version":"0.1.0"}')

        subprocess.run(
            [sys.executable, os.path.join(HERE, "sign-package.py"), manifest_path, PRIV_KEY],
            check=True,
        )
        sig_path = os.path.join(tmp, "package.sig")
        assert os.path.isfile(sig_path), "sign-package.py did not write package.sig"

        pub_key = serialization.load_pem_public_key(open(PUB_KEY, "rb").read())
        assert isinstance(pub_key, Ed25519PublicKey)
        signature = base64.b64decode(open(sig_path).read().strip())
        manifest_bytes = open(manifest_path, "rb").read()

        pub_key.verify(signature, manifest_bytes)  # raises on failure

        try:
            pub_key.verify(signature, manifest_bytes[:-1] + b"X")
            raise AssertionError("tampered manifest incorrectly verified")
        except InvalidSignature:
            pass

    print("OK: sign-package.py round trip verified (valid + tamper-rejected)")


if __name__ == "__main__":
    main()
