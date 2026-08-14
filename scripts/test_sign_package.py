#!/usr/bin/env python3
"""Self-check for sign-package.py: generate an ephemeral Ed25519 keypair,
sign a manifest with it, verify the signature against its public key, and
confirm a tampered manifest is rejected. Mirrors the exact construction
venturi-rs/crates/venturi-runtime/src/trust.rs verifies against.

The keypair is generated at test time and never touches the repo — this is an
empty scaffold with no committed publisher or private key material.

Run: python3 scripts/test_sign_package.py
"""
import base64
import os
import subprocess
import sys
import tempfile

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    private_key = Ed25519PrivateKey.generate()
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_key = private_key.public_key()

    with tempfile.TemporaryDirectory() as tmp:
        priv_path = os.path.join(tmp, "key.private.pem")
        with open(priv_path, "wb") as f:
            f.write(priv_pem)

        manifest_path = os.path.join(tmp, "package.json")
        with open(manifest_path, "wb") as f:
            f.write(b'{"package_id":"test-publisher.demo","package_version":"0.1.0"}')

        subprocess.run(
            [sys.executable, os.path.join(HERE, "sign-package.py"), manifest_path, priv_path],
            check=True,
        )
        sig_path = os.path.join(tmp, "package.sig")
        assert os.path.isfile(sig_path), "sign-package.py did not write package.sig"

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
