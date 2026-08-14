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
REGISTRY_ROOT = os.path.dirname(HERE)


def known_answer() -> None:
    """Frozen cross-implementation vector: a committed (public key, manifest,
    expected signature) triple, no private key. Ed25519 is deterministic
    (RFC 8032), so this signature is the one true answer for this key+manifest.

    This pins the wire construction the venturi host verifies against
    (venturi-rs/crates/venturi-runtime/src/trust.rs). If either side's byte
    construction drifts, this vector stops verifying and the mismatch is caught
    here instead of at install time. venturi-rs should verify the SAME vector
    from its side to close the loop across implementations.
    """
    vec = os.path.join(REGISTRY_ROOT, "conformance", "vector-1")
    pub_key = serialization.load_pem_public_key(
        open(os.path.join(vec, "public_key.pem"), "rb").read()
    )
    manifest_bytes = open(os.path.join(vec, "package.json"), "rb").read()
    signature = base64.b64decode(open(os.path.join(vec, "package.sig")).read().strip())

    pub_key.verify(signature, manifest_bytes)  # raises if the vector drifted
    try:
        pub_key.verify(signature, manifest_bytes[:-1] + b"X")
        raise AssertionError("tampered manifest incorrectly verified")
    except InvalidSignature:
        pass
    print("OK: conformance vector-1 verifies (frozen cross-impl construction)")


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
    known_answer()
    main()
