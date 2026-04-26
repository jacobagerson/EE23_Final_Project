import numpy as np
import librosa
import time
import serial

AUDIO_FILE = 'Audio_Samples/Austin Powers - Yeah baby yeah!!!.mp3'

FFT_LENGTH = 2048
HOP_LENGTH = 256
TOP_N = 20

COM_PORT = 'COM7'
BAUD_RATE = 31250

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

def send_note_on(note, velocity):
    ser.write(bytes([0x90, note, velocity]))

def send_note_off(note):
    ser.write(bytes([0x80, note, 0]))

active_notes = set()

time.sleep(0.2)

for t in range(S.shape[1]):

    mags = S[:, t].copy()

    mags[freqs > 4000] = 0
    mags[freqs < 20] = 0

    max_mag = np.max(mags) + 1e-9

    idx = np.argsort(mags)[::-1]

    current_notes = set()
    velocities = {}

    for i in idx:
        f = freqs[i]
        note = freq_to_midi(f)

        if note is None:
            continue

        mag = mags[i]

        # ✅ CORRECT PER-NOTE VELOCITY
        vel = int(np.clip(127 * (mag / max_mag), 20, 127))

        current_notes.add(note)
        velocities[note] = vel

        if len(current_notes) >= TOP_N:
            break

    # NOTE OFF
    for note in active_notes - current_notes:
        send_note_off(note)

    # NOTE ON
    for note in current_notes - active_notes:
        send_note_on(note, velocities[note])

    active_notes = current_notes

    time.sleep(FRAME_DELAY)

for note in active_notes:
    send_note_off(note)

ser.close()
