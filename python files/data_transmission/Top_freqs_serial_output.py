import numpy as np
import librosa
import time
import serial

AUDIO_FILE = 'Audio_Samples/ff-16b-2c-44100hz.mp3'

FFT_LENGTH = 2048
HOP_LENGTH = 512
TOP_N = 20
MAX_CHANGES = 6  # limit note churn per frame

COM_PORT = 'COM7'
BAUD_RATE = 115200    # match STM32

ser = serial.Serial(COM_PORT, BAUD_RATE)

y, sr = librosa.load(AUDIO_FILE, sr=None)
FRAME_DELAY = HOP_LENGTH / sr

stft = librosa.stft(y, n_fft=FFT_LENGTH, hop_length=HOP_LENGTH, center=False)
S = np.abs(stft)
freqs = librosa.fft_frequencies(sr=sr, n_fft=FFT_LENGTH)

def freq_to_midi(f):
    if f <= 0:
        return None
    return int(np.clip(librosa.hz_to_midi(f), 0, 127))

active_notes = set()

time.sleep(0.2)

for t in range(S.shape[1]):

    mags = S[:, t].copy()

    # band-limit
    mags[freqs > 4000] = 0
    mags[freqs < 20] = 0

    max_mag = np.max(mags) + 1e-9
    idx = np.argsort(mags)[::-1]

    current_notes = set()
    velocities = {}

    # pick top N notes
    for i in idx:
        f = freqs[i]
        note = freq_to_midi(f)
        if note is None:
            continue

        mag = mags[i]
        vel = int(np.clip(127 * (mag / max_mag), 20, 127))

        current_notes.add(note)
        velocities[note] = vel

        if len(current_notes) >= TOP_N:
            break

    # optional stability (reduces flicker)
    overlap = current_notes & active_notes
    if len(overlap) > TOP_N // 2:
        current_notes = overlap | current_notes

    # build batch message
    out_bytes = []
    changes = 0

    # NOTE OFF
    for note in active_notes - current_notes:
        if changes >= MAX_CHANGES:
            break
        out_bytes += [0x80, note, 0]
        changes += 1

    # NOTE ON
    for note in current_notes - active_notes:
        if changes >= MAX_CHANGES:
            break
        out_bytes += [0x90, note, velocities[note]]
        changes += 1

    # send batch
    if out_bytes:
        ser.write(bytes(out_bytes))

    active_notes = current_notes

    time.sleep(FRAME_DELAY)

# cleanup
out_bytes = []
for note in active_notes:
    out_bytes += [0x80, note, 0]

if out_bytes:
    ser.write(bytes(out_bytes))

ser.close()
