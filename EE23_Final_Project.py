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


#We have our audio file loaded and visualized


stft_result = librosa.stft(y, n_fft=FFT_LENGTH, hop_length=HOP_LENGTH)




   42
   43         print("STFT complete. Shape of the complex-valued spectrogram:", stft_result.shape)
   44
   45         # The stft_result is a complex-valued matrix where rows are frequency bins
   46         # and columns are time frames. For analysis, we convert it to a
   47         # magnitude spectrogram and often put it on a logarithmic (decibel) scale.
   48
   49         magnitude_spectrogram = np.abs(stft_result)
   50         db_spectrogram = librosa.amplitude_to_db(magnitude_spectrogram, ref=np.max)
   51
   52         print("Converted to a decibel-scaled spectrogram.")
   53
   54         # --- Visualization of the Spectrogram ---
   55         print("Plotting the spectrogram...")
   56         plt.figure(figsize=(14, 5))
   57         librosa.display.specshow(db_spectrogram, sr=sr, hop_length=HOP_LENGTH, x_axis='time', y_axis='log')
   58
   59         plt.title('Log-Frequency Power Spectrogram')
   60         plt.xlabel('Time (s)')
   61         plt.ylabel('Frequency (Hz)')
   62         plt.colorbar(format='%+2.0f dB', label='Decibels (dB)')
   63         plt.tight_layout()
   64         plt.show()


#Let's calculate the Nyquist frequency and then sample the audio file at that frequency using librosa

# nyquist_freq = sr / 2
# print(f"Nyquist Frequency: {nyquist_freq} Hz")
