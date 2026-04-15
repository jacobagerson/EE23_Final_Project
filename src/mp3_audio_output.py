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



# --- STFT/Spectrogram Parameters (Crucial for report analysis) ---
# n_fft: The length of the Fast Fourier Transform window.
# It determines the frequency resolution of the spectrogram.
# A common value is 2048.
FFT_LENGTH = 2048

# hop_length: The number of audio samples between adjacent STFT columns.
# It determines the time resolution of the spectrogram.
# A common value is 512, which is FFT_LENGTH / 4.
HOP_LENGTH = 512

# It slides a window (like a Hann window) across the audio signal, taking brief FFTs at each step. This generates a 2D spectrogram (Frequency vs. Time), giving you both the pitch and the exact timestamp, which is absolutely required to generate accurate MIDI "Note ON" and "Note OFF" events. The STFT is a powerful tool for analyzing the frequency content of audio signals over time, making it ideal for tasks like pitch detection and transcription. Necessary for generating discrete MIDI events
stft_result = librosa.stft(y, n_fft=FFT_LENGTH, hop_length=HOP_LENGTH)

magnitude_spectrogram = np.abs(stft_result)
db_spectrogram = librosa.amplitude_to_db(magnitude_spectrogram, ref=np.max)

print("STFT complete. Shape of the complex-valued spectrogram:", stft_result.shape)

plt.figure(figsize=(14, 5))
librosa.display.specshow(db_spectrogram, sr=sr, hop_length=HOP_LENGTH, x_axis='time', y_axis='log')
#    58
plt.title('Log-Frequency Power Spectrogram')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.colorbar(format='%+2.0f dB', label='Decibels (dB)')
plt.tight_layout()
plt.show()
plt.savefig('imgs/log_frequency_power_spectrogram.png', dpi=150, bbox_inches='tight')
