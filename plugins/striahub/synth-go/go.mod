module github.com/mfgmedia/stria-examples/synth-go

go 1.24

require github.com/mfgmedia/stria/sdk-go v0.1.0

// In production the SDK source is baked into the supervisor image at /app/sdk-go/.
// The builder container mounts it and applies this replace directive via GOFLAGS=-mod=mod.
replace github.com/mfgmedia/stria/sdk-go => /app/sdk-go
