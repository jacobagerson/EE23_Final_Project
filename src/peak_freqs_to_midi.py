import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import mido
import soundfile as sf

#Extract audio file, using librosa to turn it into a numpy array
audio_file_path = 'Audio_Samples/ff-16b-2c-44100hz.mp3'
filename = librosa.ex('trumpet')
y, sr = librosa.load(audio_file_path) #y is librosa time domain series


#PITCH - NOTE NUMBER

#We have our audio file loaded and visualized. The frequency domain plot will now be used to gather appropriate MIDI "Note ON" and "Note OFF" events, which will be used to generate a MIDI file. The STFT spectrogram provides the necessary information to determine the pitch and timing of each note, allowing us to create an accurate MIDI representation of the original audio.


FFT_LENGTH = 2048

# hop_length: The number of audio samples between adjacent STFT columns.
# It determines the time resolution of the spectrogram.
# A common value is 512, which is FFT_LENGTH / 4.
HOP_LENGTH = 512

#Pitch detection:

stft_result = librosa.stft(y, n_fft=FFT_LENGTH, hop_length=HOP_LENGTH)
#librosa hz -> note conversion

S = np.abs(stft_result)

# Get frequencies corresponding to each bin
freqs = librosa.fft_frequencies(sr=sr, n_fft=FFT_LENGTH)

valid_frequencies = freqs[freqs > 50]

# Find the bin with the highest magnitude for each time frame
peak_bins = np.argmax(S, axis=0)

peak_freqs = valid_frequencies[peak_bins]
peak_mags = np.max(S, axis=0)

max_loudness = np.max(peak_mags)
# Map to 0-127, round it, and ensure it's an integer
velocities = np.clip(np.round((peak_mags / max_loudness) * 127), 0, 127).astype(int)


notes = []

for j in peak_freqs:
    if j is not None:
        notes.append(librosa.hz_to_note(j, unicode=False))

midi_notes = []

print(notes[:20])

for i in notes:
    midi_notes.append(librosa.note_to_midi(i))

print(midi_notes[:20])
