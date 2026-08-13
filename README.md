# striahub

The official plugin registry for [Stria](https://github.com/mfgmedia/stria). Browse plugins at [striahub.com](https://striahub.com).

## Browse plugins

See [PLUGINS.md](PLUGINS.md) for the full registry with image tags and activity listings.

## Install a plugin

```bash
stria plugin add striahub.synth-py
```

Or pull the pre-built image directly:

```bash
docker pull ghcr.io/mfgmedia/striahub-synth-py:latest
```

## How it works

1. Plugin authors submit PRs to [striahub-submissions](https://github.com/mfgmedia/striahub-submissions)
2. Sentinel scans the code automatically
3. Approved plugins are merged here
4. CI builds a Docker image for each plugin using the official [stria runtime base images](https://github.com/mfgmedia/stria)
5. Images are pushed to `ghcr.io/mfgmedia/striahub-{name}:{version}`

## Plugin format

```
plugins/{publisher}/{name}/
├── plugin.yaml          # manifest (publisher, name, version, runtime, compatibility, provides, requires)
├── activities.py        # or main.go / index.ts / Main.java
└── README.md            # optional
```

`publisher` is a namespace slug owned by one GitHub user or org, with one Ed25519 public key.
The package id is `<publisher>.<name>`.

## Versioning

Plugins are versioned via `plugin.yaml`. Images are tagged with the version, `latest`, and the commit SHA.

## License

Individual plugins have their own licenses declared in plugin.yaml.
The registry infrastructure is proprietary — Copyright MFG Group UG.
