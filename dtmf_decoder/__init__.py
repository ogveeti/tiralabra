import sys
import wave
import struct
import math
import os
import time
import argparse

SAMPLE_RATE = 8000 # 8 kHz sampling rate, common in telephone and analog radio with ~4 kHz max. audio bandwidth.
FRAME_SIZE = 205 # ~25,6 ms window duration. Commonly chosen to align DFT frequency bins well with DTMF tone frequencies.
STEP_SIZE = 80 # Overlapped frames are processed with 10 ms stepped intervals. This is to get better timing resolution for short tones and breaks.
SILENT_FRAME_THRESHOLD = 1000  # Adjust later after testing, currently used for rough silence detection for human typed tones with long breaks.
MINIMUM_DFT_BIN_POWER = 3e6  # Adjust later after testing
DFT_BIN_POWER_RATIO_THRESHOLD = 5  # Dominant high or low frequency should be 5x stronger than the others combined, adjust later after testing.
HARMONIC_POWER_THRESHOLD = 0.3  # Second harmonic power should not exceed 30% of base tone power for a valid DTMF tone.
MINIMUM_REPEAT_FRAMES = 2  # Require two consecutive frames (20 ms) to confirm a symbol.
MINIMUM_BREAK_FRAMES = 4   # Require a four frame long tone break (40 ms) to repeat a symbol.
DTMF_FREQUENCIES = [697, 770, 852, 941, 1209, 1336, 1477, 1633] # Base frequencies.
SECOND_HARMONICS = [1394, 1540, 1704, 1882, 2418, 2672, 2954, 3266] # Second harmonics of the base frequencies.
GOERTZEL_COEFFS = {} # Global Goertzel coefficient lookup table, these are constant for each frequency bin.

# DTMF frequency pairs in Hz for each symbol.
DTMF_SYMBOLS = {
    '1': (697, 1209), '2': (697, 1336), '3': (697, 1477), 'A': (697, 1633),
    '4': (770, 1209), '5': (770, 1336), '6': (770, 1477), 'B': (770, 1633),
    '7': (852, 1209), '8': (852, 1336), '9': (852, 1477), 'C': (852, 1633),
    '*': (941, 1209), '0': (941, 1336), '#': (941, 1477), 'D': (941, 1633)
}

# Used for UI
BUTTON_LAYOUT = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]


# CLI argument parser.
def parse_args():
    parser = argparse.ArgumentParser(description="DTMF decoder")
    parser.add_argument("filepath", help="Path to WAV file")
    parser.add_argument("--realtime", action="store_true", help="Run in real-time mode (slower, simulates live input)")
    return parser.parse_args()


# Clears the terminal screen, redraws a visual button layout and prints the detected symbol sequence.
def draw_ui(detected_sequence, current_symbol=None):
    os.system('clear')  # Only works on *nix platforms, use 'cls' instead on Windows.
    print("DTMF Decoder")
    print("-" * 20)

    for row in BUTTON_LAYOUT:
        line = " "
        for key in row:
            if key == current_symbol:
                line += f"[{key}] ".ljust(5)
            else:
                line += f" {key}  ".ljust(5)
        print(line.rstrip())

    print("-" * 20)
    print(f"Detected: {detected_sequence}")
    print()


# Open, validate and read a WAV file into a list of individual real-valued PCM sample integers.
def read_wav_file(filepath):
    if not os.path.isfile(filepath):
        print("Error: File does not exist.")
        sys.exit(1)

    try:
        with wave.open(filepath, 'rb') as wav:
            nchannels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            framerate = wav.getframerate()
            num_frames = wav.getnframes()
            comptype = wav.getcomptype()

            if nchannels != 1:
                raise ValueError("Only mono files are supported.")
            if sampwidth != 2:
                raise ValueError("Only 16-bit PCM files are supported.")
            if framerate != SAMPLE_RATE:
                raise ValueError("Only 8000 Hz sample rate is supported.")
            if comptype != "NONE":
                raise ValueError("Compressed WAV files are not supported.")

            duration_sec = num_frames / SAMPLE_RATE
            if duration_sec > 180:
                raise ValueError("WAV file too long, max. 3 minutes allowed.")

            frames = wav.readframes(num_frames)
            samples = struct.unpack("<{}h".format(num_frames), frames)
            return list(samples)
    except wave.Error as e:
        raise ValueError(f"Invalid WAV file: {e}") from e


# Split the audio samples into overlapping frames using a sliding window.
def split_into_overlapping_frames(samples, frame_size, step_size, pseudo_real_time=False):
    i = 0
    total_samples = len(samples)
    while i + frame_size <= total_samples:
        frame = samples[i:i + frame_size]
        yield frame
        i += step_size
        if pseudo_real_time:
            time.sleep(step_size / SAMPLE_RATE)
    # Zero-pad and yield the last frame if needed.
    if i < total_samples:
        last_frame = samples[i:] + [0] * (frame_size - len(samples[i:]))
        yield last_frame


# Calculate the average power in each frame.
def is_silent_frame(frame, threshold):
    avg_power = sum(s ** 2 for s in frame) / len(frame)
    return avg_power < threshold


# Precalculate the coefficient terms for each target frequency bin.
def precalculate_goertzel_coeffs(frequencies, sample_rate, n):
    coeffs = {}
    for freq in frequencies:
        k = int(0.5 + (n * freq) / sample_rate)
        coeff = 2.0 * math.cos((2.0 * math.pi * k) / n)
        coeffs[freq] = coeff
    return coeffs


# Calculate the power at a specific frequency bin.
def goertzel_power(samples, freq):
    coeff = GOERTZEL_COEFFS[int(freq)] # The Goertzel coefficient works as a resonator set at a specific target frequency.

    # A delay line that stores two previous outputs of the filter:
    s_prev1 = 0
    s_prev2 = 0

    for sample in samples:
        s = sample + coeff * s_prev1 - s_prev2 # A second-order IIR filter that builds up amplitude when the input matches a target frequency due to constructive interference.
        s_prev2 = s_prev1
        s_prev1 = s
    power = s_prev2 ** 2 + s_prev1 ** 2 - coeff * s_prev1 * s_prev2 # A power detector for the filter output, calculates a squared magnitude of the complex DFT result.
    return power


# Process a single frame and identify the DTMF tone if present.
def process_frame(frame):
    # Compute powers for all DTMF frequencies.
    powers = {frequency: goertzel_power(frame, frequency) for frequency in DTMF_FREQUENCIES}

    low_freqs = DTMF_FREQUENCIES[:4]
    high_freqs = DTMF_FREQUENCIES[4:]

    # Identify the strongest frequency in low and high groups.
    low_tone = max(low_freqs, key=lambda f: powers[f])
    high_tone = max(high_freqs, key=lambda f: powers[f])

    low_power = powers[low_tone]
    high_power = powers[high_tone]

    # Compute total group power excluding the peak tone.
    low_group_total = sum(powers[f] for f in low_freqs if f != low_tone)
    high_group_total = sum(powers[f] for f in high_freqs if f != high_tone)

    # Check DFT bin power and tone power ratio thresholds.
    if (
        low_power < MINIMUM_DFT_BIN_POWER or
        high_power < MINIMUM_DFT_BIN_POWER or
        low_power / (low_group_total + 1e-10) < DFT_BIN_POWER_RATIO_THRESHOLD or # Add 1e-10 to prevent division by zero.
        high_power / (high_group_total + 1e-10) < DFT_BIN_POWER_RATIO_THRESHOLD
    ):
        return None # Reject noisy or unclear frames.

    # Check that tone does not have strong second harmonic, this is to differentiate DTMF tones from music or speech.
    for tone in (low_tone, high_tone):
        if tone in DTMF_FREQUENCIES:
            idx = DTMF_FREQUENCIES.index(tone)
            harmonic = SECOND_HARMONICS[idx]
            harmonic_power = goertzel_power(frame, harmonic)
            if harmonic_power > HARMONIC_POWER_THRESHOLD * powers[tone]:
                return None # Reject tones with strong second harmonic.


    #Lookup symbol for frequency pair.
    for symbol, (lf, hf) in DTMF_SYMBOLS.items():
        if lf == low_tone and hf == high_tone:
            return symbol # Valid frequency combination found.

    return None # Invalid frequency combinations.


def main():
    args = parse_args()
    filepath = args.filepath
    pseudo_real_time = args.realtime

    # Precalculate coefficients for both base and second harmonic frequencies.
    global GOERTZEL_COEFFS
    GOERTZEL_COEFFS = precalculate_goertzel_coeffs(DTMF_FREQUENCIES + SECOND_HARMONICS, SAMPLE_RATE, FRAME_SIZE)

    try:
        samples = read_wav_file(filepath)

        # Symbol state tracking.
        last_symbol = None
        repeat_count = 0
        printed_symbol = None
        break_frames = 0
        detected_sequence = ""

        for _, frame in enumerate(split_into_overlapping_frames(samples, FRAME_SIZE, STEP_SIZE, pseudo_real_time)):
            if is_silent_frame(frame, SILENT_FRAME_THRESHOLD):
                symbol = None # Only process non-silent frames.
            else:
                symbol = process_frame(frame)

            # Track consecutive detections of the same symbol.
            if symbol == last_symbol and symbol is not None:
                repeat_count += 1
            else:
                repeat_count = 1
                last_symbol = symbol

            # Track consecutive frames without valid tone.
            if symbol is None:
                break_frames += 1
            else:
                break_frames = 0

            # Only print a symbol if it's been detected in enough consecutive frames and not repeated.
            if repeat_count == MINIMUM_REPEAT_FRAMES and symbol != printed_symbol:
                detected_sequence += symbol
                draw_ui(detected_sequence, current_symbol=symbol)
                printed_symbol = symbol

            # Allow re-printing same symbol after enough break frames.
            if break_frames >= MINIMUM_BREAK_FRAMES:
                printed_symbol = None
                draw_ui(detected_sequence, current_symbol=None)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
