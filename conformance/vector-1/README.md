# Conformance vector-1

A frozen known-answer vector for the package-signing construction. No private
key — only the public half is committed.

| File | What it is |
|---|---|
| `package.json` | The exact manifest bytes that were signed |
| `public_key.pem` | SubjectPublicKeyInfo PEM Ed25519 **public** key |
| `package.sig` | base64 (standard, single line) of the detached Ed25519 signature over `package.json`'s exact bytes |

Ed25519 is deterministic (RFC 8032), so `package.sig` is the one true signature
for this (key, manifest) pair. The private key was generated once offline, used
to produce `package.sig`, and discarded.

**Purpose:** pin the byte-level signing construction across implementations.
`scripts/test_sign_package.py` (`known_answer()`) verifies this vector from the
Python side; `venturi-rs/crates/venturi-runtime/src/trust.rs` should verify the
same vector from the Rust side. If either construction drifts, the vector stops
verifying and the mismatch surfaces in CI instead of at a user's install time.
