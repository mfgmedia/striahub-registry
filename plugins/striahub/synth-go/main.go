// Step 2: Resonant filter sweep (Go).
//
// Go is chosen for the filter because it is a per-sample loop with no
// vectorization possible — each sample depends on the previous output.
// Python's for-loop would be 100x slower. Go compiles to native code
// and runs the loop at full CPU speed with zero GC pauses.
package main

import (
	"encoding/binary"
	"math"
	"os"
	"path/filepath"

	stria "github.com/mfgmedia/stria/sdk-go"
)

const sampleRate = 44100

func main() {
	stria.Run(map[string]stria.ActivityFunc{
		"synth.filter_sweep": filterSweep,
	})
}

func filterSweep(config, inputs map[string]any, ctx *stria.Context) (map[string]any, error) {
	samplesFile, _ := inputs["samples_file"].(string)
	startHz := floatOr(inputs, "start_hz", 200)
	endHz := floatOr(inputs, "end_hz", 8000)
	q := floatOr(inputs, "resonance", 2.0)

	// Read numpy .npy file (header + float32 array)
	samples, err := readNpy(samplesFile)
	if err != nil {
		return nil, err
	}

	n := len(samples)
	output := make([]float32, n)

	// Logarithmic frequency sweep
	logStart := math.Log(startHz)
	logEnd := math.Log(endHz)

	// One-pole low-pass with resonance feedback — per-sample loop
	var y float64
	for i := 0; i < n; i++ {
		// Sweep cutoff frequency logarithmically
		t := float64(i) / float64(n)
		freq := math.Exp(logStart + t*(logEnd-logStart))

		rc := 1.0 / (2.0 * math.Pi * freq)
		dt := 1.0 / float64(sampleRate)
		alpha := dt / (rc + dt)

		feedback := q * (y - float64(samples[i]))
		y = y + alpha*(float64(samples[i])-y+feedback*0.1)
		output[i] = float32(y)
	}

	// Normalize to prevent clipping
	var peak float32
	for _, s := range output {
		if abs := float32(math.Abs(float64(s))); abs > peak {
			peak = abs
		}
	}
	if peak > 0 {
		scale := float32(0.9) / peak
		for i := range output {
			output[i] *= scale
		}
	}

	sandbox := os.Getenv("SANDBOX_DIR")
	if sandbox == "" {
		sandbox = "/sandbox"
	}
	outPath := filepath.Join(sandbox, "filtered.npy")
	if err := writeNpy(outPath, output); err != nil {
		return nil, err
	}

	ctx.Progress(1, 1, "Filter sweep complete")
	ctx.Log("filter_applied", map[string]any{"start_hz": startHz, "end_hz": endHz, "resonance": q})

	return map[string]any{"samples_file": outPath}, nil
}

// readNpy reads a numpy .npy file containing float32 data.
// Handles the standard numpy format: 10-byte magic + header + raw data.
func readNpy(path string) ([]float32, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	// Skip numpy header: magic (6) + version (2) + header_len (2) + header string
	// Simple approach: find the newline after the header dict, data starts after
	headerEnd := 0
	for i := 10; i < len(data); i++ {
		if data[i] == '\n' {
			headerEnd = i + 1
			break
		}
	}
	raw := data[headerEnd:]
	samples := make([]float32, len(raw)/4)
	for i := range samples {
		bits := binary.LittleEndian.Uint32(raw[i*4 : i*4+4])
		samples[i] = math.Float32frombits(bits)
	}
	return samples, nil
}

// writeNpy writes float32 data as a numpy .npy file.
func writeNpy(path string, samples []float32) error {
	// Numpy header: magic + version + header
	header := "\x93NUMPY\x01\x00"
	desc := "{'descr': '<f4', 'fortran_order': False, 'shape': (" +
		itoa(len(samples)) + ",), }\n"
	// Pad header to multiple of 64 bytes
	totalLen := len(header) + 2 + len(desc)
	padding := 64 - (totalLen % 64)
	if padding == 64 {
		padding = 0
	}
	for i := 0; i < padding-1; i++ {
		desc += " "
	}
	desc += "\n"
	headerLen := len(desc)

	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()

	f.Write([]byte(header))
	binary.Write(f, binary.LittleEndian, uint16(headerLen))
	f.Write([]byte(desc))
	for _, s := range samples {
		binary.Write(f, binary.LittleEndian, s)
	}
	return nil
}

func floatOr(m map[string]any, key string, def float64) float64 {
	if v, ok := m[key]; ok {
		switch n := v.(type) {
		case float64:
			return n
		case int:
			return float64(n)
		}
	}
	return def
}

func itoa(n int) string {
	if n == 0 {
		return "0"
	}
	s := ""
	for n > 0 {
		s = string(rune('0'+n%10)) + s
		n /= 10
	}
	return s
}
