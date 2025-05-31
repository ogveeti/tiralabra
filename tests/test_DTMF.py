import math
import random
import pytest
from dtmf_decoder import (
    goertzel_power,
    is_silent_frame,
    process_frame,
    SAMPLE_RATE,
    FRAME_SIZE,
    DTMF_SYMBOLS,
    precalculate_goertzel_coeffs,
    GOERTZEL_COEFFS,
    DTMF_FREQUENCIES,
    SECOND_HARMONICS,
)

# Calculate Goertzel coefficients for all required frequencies.
def setup_module(module):
    global GOERTZEL_COEFFS
    all_freqs = DTMF_FREQUENCIES + SECOND_HARMONICS
    GOERTZEL_COEFFS.update(precalculate_goertzel_coeffs(all_freqs, SAMPLE_RATE, FRAME_SIZE))


# Generate test tones.
def generate_sine_wave(freq, amplitude=10000, frame_size=FRAME_SIZE):
    return [int(amplitude * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)) for i in range(frame_size)]


# Silent frames should be detected to be silent.
def test_silent_frame_detection():
    silent_frame = [0] * FRAME_SIZE
    assert is_silent_frame(silent_frame, threshold=1000)


# A valid DTMF frequency should be detected.
def test_goertzel_detects_valid_tone():
    freq = 770
    samples = generate_sine_wave(freq)
    power = goertzel_power(samples, freq)
    assert power > 5e11


# Other frequencies should not be detected.
def test_goertzel_ignores_wrong_frequency():
    target_freq = 770
    off_freq = 800  #Not a DTMF tone
    samples = generate_sine_wave(off_freq)
    power = goertzel_power(samples, target_freq)
    assert power < 5e11


# A frame full of DC signal has energy but should not be detected as symbols.
def test_process_frame_rejects_dc():
    dc = [5000] * FRAME_SIZE
    assert process_frame(dc) is None


# White noise should not be detected as symbols.
def test_process_frame_rejects_white_noise():
    noise = [random.randint(-5000, 5000) for _ in range(FRAME_SIZE)]
    assert process_frame(noise) is None


# All valid DTMF frequency pairs should be detected as symbols.
@pytest.mark.parametrize("symbol, low_freq, high_freq", [
    ('1', 697, 1209), ('2', 697, 1336), ('3', 697, 1477), ('A', 697, 1633),
    ('4', 770, 1209), ('5', 770, 1336), ('6', 770, 1477), ('B', 770, 1633),
    ('7', 852, 1209), ('8', 852, 1336), ('9', 852, 1477), ('C', 852, 1633),
    ('*', 941, 1209), ('0', 941, 1336), ('#', 941, 1477), ('D', 941, 1633),
])
def test_process_frame_detects_dtmf_symbol(symbol, low_freq, high_freq):
    samples = [
        int(5000 * (
            math.sin(2 * math.pi * low_freq * i / SAMPLE_RATE) +
            math.sin(2 * math.pi * high_freq * i / SAMPLE_RATE)
        ))
        for i in range(FRAME_SIZE)
    ]
    assert process_frame(samples) == symbol
