import numpy as np
import matplotlib.pyplot as plt
import librosa
import seaborn as sns

# -------------------------------
# Load audio
# -------------------------------
audio_file_path = 'Audio_Samples/ff-16b-2c-44100hz.mp3'
y, sr = librosa.load(audio_file_path)

# -------------------------------
# STFT
# -------------------------------
FFT_LENGTH = 2048
HOP_LENGTH = 512

stft_result = librosa.stft(y, n_fft=FFT_LENGTH, hop_length=HOP_LENGTH)
S = np.abs(stft_result)

freqs = librosa.fft_frequencies(sr=sr, n_fft=FFT_LENGTH)
times = np.arange(S.shape[1]) * (HOP_LENGTH / sr)

# -------------------------------
# Sort bins by magnitude
# -------------------------------
sorted_bins = np.argsort(S, axis=0)

# -------------------------------
# Rank bands (10 each)
# -------------------------------
bands = [(i, i+10) for i in range(0, 100, 10)]

# -------------------------------
# FIGURE 1: Time vs MIDI
# -------------------------------
fig_time, axes_time = plt.subplots(
    5, 2,
    figsize=(12, 18),
    constrained_layout=True
)
axes_time = axes_time.flatten()

# -------------------------------
# FIGURE 2: KDE plots
# -------------------------------
fig_kde, axes_kde = plt.subplots(
    5, 2,
    figsize=(12, 18),
    constrained_layout=True
)
axes_kde = axes_kde.flatten()

# -------------------------------
# Loop through bands
# -------------------------------
for i, (low, high) in enumerate(bands):

    # Select band
    band_bins = sorted_bins[-high:-low if low != 0 else None, :]
    band_freqs = freqs[band_bins]

    # Convert to MIDI
    midi_notes = 69 + 12 * np.log2(band_freqs / 440.0)
    midi_notes = np.nan_to_num(midi_notes)
    midi_notes = np.round(midi_notes).astype(int)

    # -------------------------------
    # PLOT 1: Time scatter (cleaned)
    # -------------------------------
    downsample = 10

    for k in [0, 4, 9]:  # representative ranks
        axes_time[i].scatter(
            times[::downsample],
            midi_notes[k][::downsample],
            s=3,
            alpha=0.6,
            label=f"Rank {low+k+1}"
        )

    axes_time[i].set_title(f"Rank {low+1}–{high}", fontsize=10, pad=10)
    axes_time[i].set_ylim(0, 127)
    axes_time[i].grid(True)

    if i < 2:
        axes_time[i].legend(fontsize=7)

    # -------------------------------
    # PLOT 2: KDE (cleaned)
    # -------------------------------
    colors = plt.cm.plasma(np.linspace(0, 1, band_freqs.shape[0]))

    for k in [0, 4, 9]:  # representative ranks
        sns.kdeplot(
            band_freqs[k],
            ax=axes_kde[i],
            color=colors[k],
            linewidth=2,
            bw_adjust=0.6,
            label=f"Rank {low+k+1}"
        )

    axes_kde[i].set_title(f"Rank {low+1}–{high}", fontsize=10, pad=10)
    axes_kde[i].set_xlabel("Frequency (Hz)")
    axes_kde[i].set_ylabel("Density")

    if i < 2:
        axes_kde[i].legend(fontsize=7)

# -------------------------------
# Global labels
# -------------------------------
fig_time.supxlabel("Time (seconds)")
fig_time.supylabel("MIDI Note")
fig_time.suptitle(
    "Pitch Structure by Peak Rank (Bands of 10)",
    fontsize=16,
    y=1.02
)

fig_kde.suptitle(
    "Frequency Distribution by Rank Band (KDE)",
    fontsize=16,
    y=1.02
)

# -------------------------------
# Show plots
# -------------------------------
plt.show()
