// Step 3: LFO amplitude modulation — tremolo effect (TypeScript).
//
// TypeScript is chosen because Node.js TypedArrays (Float32Array) handle
// array math efficiently, and the async SDK is natural for Node.js.
// This is array-level math (no per-sample loop), so TS performance is fine.

import { run, type ActivityFunc } from 'stria'
import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const SAMPLE_RATE = 44100

const lfoAmplitude: ActivityFunc = async (config, inputs, ctx) => {
  const samplesFile = inputs.samples_file as string
  const rate = (inputs.lfo_rate_hz as number) ?? 4.0
  const depth = (inputs.depth as number) ?? 0.5

  // Read numpy .npy (skip header, read float32 array)
  const raw = readFileSync(samplesFile)
  const headerEnd = raw.indexOf(0x0a, 10) + 1 // newline after header dict
  const data = new Float32Array(raw.buffer, raw.byteOffset + headerEnd)

  const n = data.length
  const output = new Float32Array(n)

  // LFO: oscillates between (1-depth) and 1.0
  for (let i = 0; i < n; i++) {
    const t = i / SAMPLE_RATE
    const lfo = 1.0 - depth * 0.5 * (1.0 + Math.sin(2 * Math.PI * rate * t))
    output[i] = data[i] * lfo
  }

  const sandbox = process.env.SANDBOX_DIR ?? '/sandbox'
  const outPath = join(sandbox, 'lfo_mod.npy')

  // Write numpy .npy
  const header = "\x93NUMPY\x01\x00"
  const desc = `{'descr': '<f4', 'fortran_order': False, 'shape': (${n},), }\n`
  const padLen = 64 - ((header.length + 2 + desc.length) % 64)
  const paddedDesc = desc.slice(0, -1) + ' '.repeat(padLen > 0 ? padLen - 1 : 0) + '\n'
  const headerLenBuf = Buffer.alloc(2)
  headerLenBuf.writeUInt16LE(paddedDesc.length)

  const npyHeader = Buffer.concat([
    Buffer.from(header, 'binary'),
    headerLenBuf,
    Buffer.from(paddedDesc),
  ])
  const outBuf = Buffer.concat([npyHeader, Buffer.from(output.buffer)])
  writeFileSync(outPath, outBuf)

  ctx.progress(1, 1, `LFO tremolo at ${rate} Hz, depth=${depth}`)
  ctx.log('lfo_applied', { lfo_rate_hz: rate, depth })

  return { samples_file: outPath }
}

const exportFile: ActivityFunc = async (_config, inputs, ctx) => {
  const mp3File = inputs.mp3_file as string
  const { statSync } = await import('node:fs')
  const stat = statSync(mp3File)

  ctx.progress(1, 1, `Export ready: ${mp3File} (${stat.size} bytes)`)
  ctx.log('file_exported', { path: mp3File, size_bytes: stat.size, format: 'mp3' })

  // In production: upload to S3, write to DB
  return {
    file_path: mp3File,
    file_size: stat.size,
    format: 'mp3',
    sample_rate: SAMPLE_RATE,
  }
}

run({
  'synth.lfo_amplitude': lfoAmplitude,
  'synth.export_file': exportFile,
})
