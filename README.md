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

## License

Individual plugins have their own licenses declared in plugin.yaml.
The registry infrastructure is proprietary — Copyright MFG Group UG.
