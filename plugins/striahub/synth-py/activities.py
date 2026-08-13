"""Step 1: Sine wave generator (Python + NumPy).

Python is the natural choice for signal generation — np.sin on a linspace
array is one line of code. No other language does this as concisely.
"""

import os
import numpy as np
from stria import activity, ActivityContext

SAMPLE_RATE = 44100
SANDBOX = os.environ.get("SANDBOX_DIR", "/sandbox")


@activity("synth.generate_sine")
def generate_sine(config: dict, inputs: dict, ctx: ActivityContext) -> dict:
    freq = float(inputs.get("frequency_hz", 440))
    dur = float(inputs.get("duration_s", 3))
    amp = float(inputs.get("amplitude", 0.8))

    num_samples = int(SAMPLE_RATE * dur)
    t = np.linspace(0, dur, num_samples, dtype=np.float32)
    samples = (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)

    out_path = os.path.join(SANDBOX, "sine.npy")
    np.save(out_path, samples)

    ctx.progress(1, 1, f"Generated {dur}s sine at {freq} Hz")
    ctx.log("sine_generated", {"frequency_hz": freq, "duration_s": dur, "num_samples": num_samples})

    return {"samples_file": out_path, "sample_rate": SAMPLE_RATE, "num_samples": num_samples}
