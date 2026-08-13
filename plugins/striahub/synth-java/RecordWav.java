// Step 4: WAV recorder (Java).
//
// Java is chosen for binary format writing because ByteBuffer with
// little-endian byte order is purpose-built for struct packing.
// WAV is a RIFF container with precise byte-level layout — Java's
// explicit buffer management is cleaner than Python's struct.pack.

package synth;

import eu.mfgmedia.stria.Stria;
import eu.mfgmedia.stria.ActivityContext;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

public class RecordWav {

    static final int SAMPLE_RATE = 44100;

    public static void main(String[] args) {
        Stria.run(Map.of("synth.record_wav", RecordWav::recordWav));
    }

    static Map<String, Object> recordWav(
            Map<String, Object> config,
            Map<String, Object> inputs,
            ActivityContext ctx) throws Exception {

        String samplesFile = (String) inputs.get("samples_file");
        String filename = inputs.getOrDefault("filename", "output.wav").toString();

        // Read numpy .npy float32 array
        byte[] raw = Files.readAllBytes(Path.of(samplesFile));
        int headerEnd = findNewline(raw, 10) + 1;
        int numSamples = (raw.length - headerEnd) / 4;

        // Convert float32 → int16 PCM
        ByteBuffer floatBuf = ByteBuffer.wrap(raw, headerEnd, raw.length - headerEnd)
                .order(ByteOrder.LITTLE_ENDIAN);
        byte[] pcmData = new byte[numSamples * 2];
        ByteBuffer pcmBuf = ByteBuffer.wrap(pcmData).order(ByteOrder.LITTLE_ENDIAN);

        for (int i = 0; i < numSamples; i++) {
            float sample = floatBuf.getFloat();
            short int16 = (short) Math.max(-32768, Math.min(32767, sample * 32767));
            pcmBuf.putShort(int16);
        }

        // Write WAV file with RIFF header
        String sandbox = System.getenv("SANDBOX_DIR");
        if (sandbox == null) sandbox = "/sandbox";
        Path wavPath = Path.of(sandbox, filename);

        try (OutputStream out = new BufferedOutputStream(Files.newOutputStream(wavPath))) {
            ByteBuffer header = ByteBuffer.allocate(44).order(ByteOrder.LITTLE_ENDIAN);

            // RIFF header
            header.put("RIFF".getBytes());
            header.putInt(36 + pcmData.length);
            header.put("WAVE".getBytes());

            // fmt chunk
            header.put("fmt ".getBytes());
            header.putInt(16);           // chunk size
            header.putShort((short) 1);  // PCM format
            header.putShort((short) 1);  // mono
            header.putInt(SAMPLE_RATE);
            header.putInt(SAMPLE_RATE * 2); // byte rate
            header.putShort((short) 2);  // block align
            header.putShort((short) 16); // bits per sample

            // data chunk
            header.put("data".getBytes());
            header.putInt(pcmData.length);

            out.write(header.array());
            out.write(pcmData);
        }

        double duration = (double) numSamples / SAMPLE_RATE;
        ctx.progress(1, 1, String.format("Recorded %.1fs WAV → %s", duration, filename));
        ctx.log("wav_recorded", Map.of("path", wavPath.toString(), "duration_s", duration));

        return Map.of("wav_file", wavPath.toString());
    }

    private static int findNewline(byte[] data, int start) {
        for (int i = start; i < data.length; i++) {
            if (data[i] == '\n') return i;
        }
        return data.length - 1;
    }
}
