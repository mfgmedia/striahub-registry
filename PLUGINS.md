# striahub Plugin Registry

> Browse at [striahub.com](https://striahub.com) | Install via `stria plugin add <name>`

## Plugins

| Plugin | Publisher | Runtime | Version | Provides | Deps | Image |
|--------|-----------|---------|---------|----------|------|-------|
| [greeter](plugins/striahub/greeter/) | striahub | python | 1.0.0 | `example.greet`, `example.uppercase` | — | `ghcr.io/mfgmedia/striahub-greeter:latest` |
| [synth-py](plugins/striahub/synth-py/) | striahub | python | 1.0.0 | `synth.generate_sine` | numpy | `ghcr.io/mfgmedia/striahub-synth-py:latest` |
| [synth-go](plugins/striahub/synth-go/) | striahub | go | 1.0.0 | `synth.filter_sweep` | — | `ghcr.io/mfgmedia/striahub-synth-go:latest` |
| [synth-ts](plugins/striahub/synth-ts/) | striahub | node | 1.0.0 | `synth.lfo_amplitude`, `synth.export_file` | — | `ghcr.io/mfgmedia/striahub-synth-ts:latest` |
| [synth-java](plugins/striahub/synth-java/) | striahub | java | 1.0.0 | `synth.record_wav` | — | `ghcr.io/mfgmedia/striahub-synth-java:latest` |
| [synth-ffmpeg](plugins/striahub/synth-ffmpeg/) | striahub | system | 1.0.0 | `synth.encode_mp3` | ffmpeg (binary) | — |

## Image naming

Plugin images follow the pattern:
```
ghcr.io/mfgmedia/striahub-{plugin-name}:{version}
```

Tags available:
- `:latest` — latest main branch build
- `:X.Y.Z` — pinned to plugin version
- `:sha-{commit}` — pinned to exact commit

## Adding a plugin

Submit a PR to [striahub-submissions](https://github.com/mfgmedia/striahub-submissions). Sentinel scans automatically. Approved plugins are merged here and images are built by CI.

## Runtime base images

Plugin images are built on top of the official stria runtime base images:

| Runtime | Base image |
|---------|-----------|
| Python | `ghcr.io/mfgmedia/stria-runtime-python:main` |
| Node.js | `ghcr.io/mfgmedia/stria-runtime-node:main` |
| Java | `ghcr.io/mfgmedia/stria-runtime-java:main` |
| Go | `ghcr.io/mfgmedia/stria-runtime-go:main` |
