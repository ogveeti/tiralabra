import sys
import wave
import struct
import math
import os

SAMPLE_RATE = 8000 #8 kHz sampling rate, common in telephone and analog radio with ~4 kHz max. audio bandwidth.
FRAME_SIZE = 205 #~25,6 ms window duration. Commonly chosen to align DFT frequency bins well with DTMF tone frequencies.
STEP_SIZE = 80 #Overlapped frames are processed with 10 ms stepped intervals. This is to get better timing resolution for short tones and breaks.
SILENCE_ENERGY_THRESHOLD = 1000  #Adjust later after testing, currently used for rough silence detection for human typed tones with long breaks.


#Open, validate and read a WAV file into a list of individual real-valued PCM sample integers.
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
        raise ValueError(f"Invalid WAV file: {e}")


#Split the audio samples into overlapping frames for processing frame-by-frame.
#This implementation stores a lot of duplicate data and delays processing until all frames are prepared.
#TODO: Implement a sliding window approach to process frames on the fly and reduce extra memory use.
def split_into_overlapping_frames(samples, frame_size, step_size):
    frames = []
    for i in range(0, len(samples) - frame_size + 1, step_size):
        frame = samples[i:i + frame_size]
        frames.append(frame)
    #Zero-pad the last frame if needed.
    last_start = len(samples) - frame_size
    if len(samples) % step_size != 0 and last_start > 0:
        last_frame = samples[last_start:]
        last_frame += [0] * (frame_size - len(last_frame))
        frames.append(last_frame)
    return frames


#Calculate the spectral energy in each frame.
def is_silent_frame(frame, threshold):
    energy = sum(s ** 2 for s in frame) / len(frame)
    return energy < threshold


#Placeholder for Goertzel frequency detection, the function will process a single frame and detect DTMF tones.
#Detected tones could be returned as a character or None.
#TODO: Implement Goertzel algorithm here
def process_frame(frame):
    return "[?]"  #Placeholder symbol


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_wav>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        samples = read_wav_file(filepath)
        frames = split_into_overlapping_frames(samples, FRAME_SIZE, STEP_SIZE)

        #Only process non-silent frames.
        for idx, frame in enumerate(frames):
            if is_silent_frame(frame, SILENCE_ENERGY_THRESHOLD):
                print(f"Frame {idx}: Silence / below threshold")
            else:
                symbol = process_frame(frame)
                print(f"Frame {idx}: Detected symbol {symbol}")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
