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

#Let's view the audio file as a waveform both in time and frequency domain, using librosa's display module

#Time Domain Plot
plt.figure(figsize=(12, 4))
librosa.display.waveshow(y, sr=sr)
plt.title('Audio Waveform')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.tight_layout()
plt.savefig('imgs/time_domain_beginning_waveform.png', dpi=150, bbox_inches='tight')
plt.show()

#Frequency Domain Plot
D = librosa.stft(y)
S_db = librosa.power_to_db(np.abs(D)**2, ref=np.max)

plt.figure(figsize=(12, 4))
librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log')
plt.title('Spectrogram (Power Spectrum)')
plt.colorbar(label='Power (dB)')
plt.tight_layout()
plt.savefig('imgs/frequency_domain_beginning_waveform.png', dpi=150, bbox_inches='tight')
plt.show()

#Let's calculate the Nyquist frequency and then sample the audio file at that frequency using librosa

nyquist_freq = sr / 2
print(f"Nyquist Frequency: {nyquist_freq} Hz")
