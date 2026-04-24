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

#ignoring all frequencies below F frequencies
cuttoff_freq = 10
valid_idx = freqs > cuttoff_freq
valid_frequencies = freqs[valid_idx]
S_valid = S[valid_idx, :]

# Find the bin with the highest magnitude for each time frame
peak_bins = np.argmax(S_valid, axis=0)

peak_freqs = valid_frequencies[peak_bins]
peak_mags = np.max(S_valid, axis=0)

max_loudness = np.max(peak_mags)
# Map to 0-127, round it, and ensure it's an integer
velocities = np.clip(np.round((peak_mags / max_loudness) * 127), 0, 127).astype(int)

notes = []

for j in peak_freqs:
    if j is not None:
        notes.append(librosa.hz_to_note(j, unicode=False))

midi_notes = []

for i in notes:
    midi_notes.append(librosa.note_to_midi(i))


for i in range(3000):
    print("midi note: ", str(midi_notes[i]))
    print("Velocity", str(velocities[i]))


# print("Confirming alignment \n")
# print(len(midi_notes))
# print(len(velocities))

times = np.arange(len(midi_notes)) * (HOP_LENGTH / sr)

plt.figure(figsize=(12, 5))
plt.scatter(times, midi_notes, s=5)
plt.xlabel("Time (seconds)")
plt.ylabel("MIDI Note")
plt.title(f"Pitch (MIDI Notes) Over Time With {cuttoff_freq} Hz Cutoff")

plt.grid(True)
#plt.show()

midi_events = []

for note, velocity in zip(midi_notes, velocities):
    if velocity > 10:
        event = [0x90, int(note), int(velocity)] # Note ON 
    else:
        event = [0x80, int(note), int(velocity)] #Note off
    midi_events.append(event)

# Create a MIDI file and add the events
midi_file = mido.MidiFile()
track = mido.MidiTrack()
midi_file.tracks.append(track)

#DUMB HUMAN IMPLEMENTATION - NOT TIMING CORRECT
for j in midi_events:
    track.append(mido.Message.from_bytes(j))
    print(mido.Message.from_bytes(j))


#AI SUGGESTED TIMING IMPLEMENTATION 
# # --- 1. SETUP TIMING ---
# # Standard MIDI defaults: 120 BPM
# tempo = mido.bpm2tempo(120) 
# ticks_per_beat = midi_file.ticks_per_beat

# # Calculate how many seconds each STFT frame represents
# seconds_per_frame = HOP_LENGTH / sr

# # Convert those seconds into MIDI ticks
# ticks_per_frame = mido.second2tick(seconds_per_frame, ticks_per_beat, tempo)

# # --- 2. TRACK STATE AND ACCUMULATE TIME ---
# active_note = None
# accumulated_ticks = 0

# for note, velocity in zip(midi_notes, velocities):
#     # Determine the current note based on your velocity threshold
#     current_note = int(note) if velocity > 10 else None

#     # Check if the note has changed (a new pitch, a rest started, or a note ended)
#     if current_note != active_note:
        
#         # Turn OFF the previous note if one was playing
#         if active_note is not None:
#             track.append(mido.Message('note_off', note=active_note, velocity=0, time=int(accumulated_ticks)))
#             accumulated_ticks = 0 # Reset delta time immediately after sending a message
        
#         # Turn ON the new note
#         if current_note is not None:
#             track.append(mido.Message('note_on', note=current_note, velocity=int(velocity), time=int(accumulated_ticks)))
#             accumulated_ticks = 0 # Reset delta time immediately after sending a message

#         active_note = current_note

#     # Advance time by one STFT frame for the next iteration
#     accumulated_ticks += ticks_per_frame

# # Turn off the very last note if it's still playing at the end of the audio file
# if active_note is not None:
#     track.append(mido.Message('note_off', note=active_note, velocity=0, time=int(accumulated_ticks)))


# Save the file
midi_file.save('output.mid')
print("MIDI file saved successfully!")