import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from scipy.signal import butter, filtfilt

# ==============================
# CONFIG
# ==============================

WAV_FILE = "Data/Austin_Powers_Spectrogram(topN20).wav"

FFT_LENGTH = 2048
HOP_LENGTH = 256   # must match generator

# ==============================
# LOAD WAV
# ==============================

y, sr = librosa.load(WAV_FILE, sr=None, mono=True)

print(f"Sample rate: {sr}")
print(f"Samples: {len(y)}")

# ==============================
# CLEAN SIGNAL (IMPORTANT)
# ==============================

# Remove DAC DC offset
y = y - np.mean(y)

# Normalize safely
y = y / (np.max(np.abs(y)) + 1e-9)

# 🔥 HIGH-PASS FILTER (kills that huge low band)
def highpass(data, cutoff=50, fs=sr, order=4):
    b, a = butter(order, cutoff / (0.5 * fs), btype='high')
    return filtfilt(b, a, data)

# 🔥 LOW-PASS FILTER (optional, cleans noise)
def lowpass(data, cutoff=2000, fs=sr, order=4):
    b, a = butter(order, cutoff / (0.5 * fs), btype='low')
    return filtfilt(b, a, data)

y = highpass(y, 50)
y = lowpass(y, 2000)

# ==============================
# STFT
# ==============================

stft = librosa.stft(
    y,
    n_fft=FFT_LENGTH,
    hop_length=HOP_LENGTH,
    center=False
)

S = np.abs(stft)

# 🔥 BETTER CONTRAST (this matters a lot)
S_db = librosa.amplitude_to_db(S, ref=np.max)

# ==============================
# PLOT
# ==============================

plt.figure(figsize=(14, 6))

librosa.display.specshow(
    S_db,
    sr=sr,
    hop_length=HOP_LENGTH,
    x_axis='time',
    y_axis='linear',
    cmap='magma',
    vmin=-70,   # 🔥 tighter dynamic range
    vmax=0
)

plt.ylim(0, 2000)

plt.colorbar(label="dB")
plt.title("Reconstructed Audio Spectrogram (DAC Output)")
plt.xlabel("Time (s)")
plt.ylabel("Frequency (Hz)")

plt.tight_layout()
plt.show()
