import numpy as np
import librosa
import time
import serial

# ==============================
# CONFIG
# ==============================

AUDIO_FILE = 'Audio_Samples/ff-16b-2c-44100hz.mp3'
FFT_LENGTH = 2048
HOP_LENGTH = 512
TOP_N = 50

COM_PORT = 'COM7'   # CHANGE THIS
BAUD_RATE = 115200   # MIDI standard baud rate

FRAME_DELAY = HOP_LENGTH / 44100.0  # seconds per frame

# ==============================
# INIT SERIAL
# ==============================

ser = serial.Serial(COM_PORT, BAUD_RATE)

# ==============================
# LOAD AUDIO
# ==============================

y, sr = librosa.load(AUDIO_FILE)

# ==============================
# STFT
# ==============================

stft = librosa.stft(y, n_fft=FFT_LENGTH, hop_length=HOP_LENGTH)
S = np.abs(stft)

freqs = librosa.fft_frequencies(sr=sr, n_fft=FFT_LENGTH)

# ==============================
# MIDI HELPERS
# ==============================

def freq_to_midi(f):
    if f <= 0:
        return None
    return int(np.clip(librosa.hz_to_midi(f), 0, 127))

def send_note_on(note, velocity=100):
    msg = bytes([0x90, note, velocity])
    ser.write(msg)
    print(f"NOTE ON  | note={note:3d} vel={velocity:3d} | bytes={list(msg)}")


def send_note_off(note):
    msg = bytes([0x80, note, 0])
    ser.write(msg)
    print(f"NOTE OFF | note={note:3d} vel=  0 | bytes={list(msg)}")

# ==============================
# PROCESS + STREAM
# ==============================

prev_notes = set()

for t in range(S.shape[1]):

    mags = S[:, t].copy()

    # kill high freq noise
    mags[freqs > 400] = 0

    # top N peaks
    peak_indices = np.argpartition(mags, -TOP_N)[-TOP_N:]
    peak_indices = peak_indices[np.argsort(mags[peak_indices])[::-1]]

    current_notes = set()

    for idx in peak_indices:
        f = freqs[idx]
        midi_note = freq_to_midi(f)

        if midi_note is not None:
            current_notes.add(midi_note)

    # ==============================
    # NOTE OFF (anything no longer active)
    # ==============================
    for note in prev_notes - current_notes:
        send_note_off(note)

    # ==============================
    # NOTE ON (new notes)
    # ==============================
    for note in current_notes - prev_notes:
        send_note_on(note, velocity=100)

    prev_notes = current_notes

    # simulate real-time playback
    time.sleep(FRAME_DELAY)

# turn everything off at end
for note in prev_notes:
    send_note_off(note)

ser.close()
