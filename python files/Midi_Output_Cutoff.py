import numpy as np
import matplotlib.pyplot as plt
import librosa
import os
from datetime import datetime

# -------------------------------
# Setup
# -------------------------------
os.makedirs("imgs", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

audio_file_path = 'Audio_Samples/ff-16b-2c-44100hz.mp3'
y, sr = librosa.load(audio_file_path)

# -------------------------------
# STFT
# -------------------------------
FFT_LENGTH = 2048
HOP_LENGTH = 512

S = np.abs(librosa.stft(y, n_fft=FFT_LENGTH, hop_length=HOP_LENGTH))
freqs = librosa.fft_frequencies(sr=sr, n_fft=FFT_LENGTH)

times = np.arange(S.shape[1]) * (HOP_LENGTH / sr)

# Sort bins by magnitude
sorted_bins = np.argsort(S, axis=0)

# -------------------------------
# Parameters
# -------------------------------
BAND_SIZE = 50
NUM_BANDS = 10   # 1–50, 51–100, ..., 451–500

# -------------------------------
# Create figure
# -------------------------------
fig, axes = plt.subplots(
    NUM_BANDS, 1,
    figsize=(12, 14),
    sharex=True
)

# -------------------------------
# Loop over bands
# -------------------------------
for b in range(NUM_BANDS):

    low = b * BAND_SIZE
    high = (b + 1) * BAND_SIZE

    # Extract bins for this band
    band_bins = sorted_bins[-high:-low if low != 0 else None, :]
    band_freqs = freqs[band_bins]

    # Convert to MIDI safely
    safe = np.where(band_freqs <= 0, np.nan, band_freqs)

    midi = 69 + 12 * np.log2(safe / 440.0)
    midi = np.nan_to_num(midi)

    # Plot heatmap
    axes[b].imshow(
        midi,
        aspect='auto',
        origin='lower',
        extent=[times[0], times[-1], low+1, high],
        cmap='viridis',
        vmin=40,
        vmax=100
    )

    # Side label instead of title
    axes[b].set_ylabel(f"{low+1}-{high}", rotation=0, labelpad=30)

# -------------------------------
# Clean formatting
# -------------------------------
for ax in axes[:-1]:
    ax.set_xticklabels([])

axes[-1].set_xlabel("Time (seconds)")

fig.suptitle("Pitch Structure by Rank Bands (50 per band)", fontsize=14)

fig.tight_layout(rect=[0.08, 0, 1, 0.96])



plt.show()
