# striahub-registry

The plugin registry for [Stria](https://github.com/filiumio/stria-rs). This is a
clean scaffold: the registry machinery (publisher trust anchors, package signing,
CI image builds) with no plugins published yet.

## Publishers

`publishers/<slug>/` is the authoritative publisher → key mapping — the production
trust-anchor namespace. One publisher per directory, **public material only**:

```
publishers/<slug>/
├── key.pem           # PKCS#8 PEM Ed25519 PUBLIC key — the trust anchor, hashed by hosts
│                      # (its sha256 is what the host's trust config pins)
└── claim.json         # records the GitHub owner (slug, github_login, github_user_id, ...)
```

A promotion is a signed commit adding or updating a publisher's `key.pem`/`claim.json`
here. `scripts/check-no-private-keys.sh` fails the repo if any private key material
ever lands under `publishers/` — private keys are never trust anchors and never belong
in this namespace.

## Signing a package manifest

```bash
python3 scripts/sign-package.py <package_dir>/package.json <path-to-private-key>.pem
```

Writes `<package_dir>/package.sig`: base64 (standard alphabet, single line) of the
detached Ed25519 signature over the manifest file's exact bytes. This is byte-for-byte
the construction the venturi host verifies against
(`venturi-rs/crates/venturi-runtime/src/trust.rs`, `verify()` step 6) — same base64
engine, same "sign the raw bytes read from disk, no re-encoding" rule.

## Plugin format

Each plugin follows the Stria plugin convention:

```
plugins/{name}/
├── plugin.yaml          # manifest (name, version, provides, requires)
├── templates/           # templates
├── activities.py        # or main.go / index.ts / *.java
└── README.md
```

On push to `main`, CI (`.github/workflows/build-plugin-images.yml`) builds a container
image for each changed plugin on the appropriate
`ghcr.io/filiumio/stria-rs-runtime-<lang>` base and pushes it to
`ghcr.io/filiumio/striahub-<name>`.

## Local checks

```bash
scripts/check-no-private-keys.sh       # fails if private key material is under publishers/
python3 scripts/test_sign_package.py   # signing round-trip self-check (ephemeral keypair)
```
