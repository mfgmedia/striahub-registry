# striahub

The official plugin registry for Stria (caudate). Every plugin here has been
scanned and approved by Sentinel.

## Installation

Plugins are installed via git sparse checkout. Each tenant checks out only
the plugins they're subscribed to:

```bash
git clone --no-checkout --filter=blob:none https://github.com/mfgmedia/striahub.git
cd striahub
git sparse-checkout init --cone
git sparse-checkout set plugins/sentinel-extractor plugins/rag-indexer
git checkout main
```

## Adding a new plugin

Submit to [striahub-submissions](https://github.com/mfgmedia/striahub-submissions).
Sentinel scans automatically. Approved plugins are ported here.

## Plugin format

Each plugin follows the Stria plugin convention:

```
plugins/{name}/
├── plugin.yaml          # manifest (name, version, provides, requires)
├── templates/           # caudate/v2 templates
├── activities.py        # or main.go / index.ts
└── README.md
```

## Versioning

Plugins are versioned via prefixed git tags: `{plugin-name}/v{semver}`

```bash
# Pin to a specific version
git fetch --tags
git checkout sentinel-extractor/v1.2.0 -- plugins/sentinel-extractor/
```

## Publishers

`publishers/<slug>/` is the authoritative publisher → key mapping (shared package contract,
`filium-sales/docs/contracts/package-model.md` §5.1) — the production trust-anchor namespace.
One publisher per directory, **public material only**:

```
publishers/<slug>/
├── key.pem           # PKCS#8 PEM Ed25519 PUBLIC key — the trust anchor, hashed by hosts
│                      # (its sha256 is what `trust.toml`'s `public_key_sha256` pins)
└── claim.json         # records the GitHub owner (slug, github_login, github_user_id, ...)
```

A promotion is a signed commit adding or updating a publisher's `key.pem`/`claim.json` here.
`striahub.com`'s `striahub.publishers` table is a cache of this git state, never the source of
truth. `scripts/check-no-private-keys.sh` fails the repo if any private key material ever lands
under `publishers/` — run it locally before pushing (see "CI / local checks" below).

Private keys never live under `publishers/`. They live under `testkeys/<slug>/`:

```
testkeys/<slug>/
└── key.private.pem   # PKCS#8 PEM Ed25519 PRIVATE key — never a trust anchor
```

`publishers/test-publisher/` is a **TEST-ONLY seed publisher**: a freshly generated Ed25519
keypair with no real GitHub claim behind it, used to exercise the promotion/signing/verification
path end to end (see `scripts/sign-package.py`). Its matching private half lives at
`testkeys/test-publisher/key.private.pem` — committed on purpose, headed `TEST-ONLY`, mirroring
the fixture-key precedent in package-model.md §6.4, but kept out of the `publishers/` trust-anchor
namespace so it can never be mistaken for a real one. This whole entry is replaced outright at the
first real publisher promotion; it is never extended with real publisher data.

## Signing a package manifest

```bash
python3 scripts/sign-package.py <package_dir>/package.json testkeys/<slug>/key.private.pem
```

Writes `<package_dir>/package.sig`: base64 (standard alphabet, single line) of the detached
Ed25519 signature over the manifest file's exact bytes. This is byte-for-byte the construction the
venturi host verifies against (`venturi-rs/crates/venturi-runtime/src/trust.rs`, `verify()` step 6)
— same base64 engine, same "sign the raw bytes read from disk, no re-encoding" rule.

## CI / local checks

This repo has no GitHub Actions workflow yet. Until one exists, run these before pushing:

```bash
scripts/check-no-private-keys.sh   # fails if private key material is under publishers/
python3 scripts/test_sign_package.py   # signing round-trip self-check
```

## License

Individual plugins have their own licenses declared in plugin.yaml.
The registry infrastructure is proprietary — Copyright MFG Group UG.
