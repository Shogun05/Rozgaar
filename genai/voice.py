import speech_recognition as sr
from pydub import AudioSegment

# Function to convert MP3 to WAV
def convert_mp3_to_wav(mp3_file, wav_file):
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format="wav")

# Convert the .mp3 file to .wav
mp3_file = "audio.mp3"  # Path to your MP3 file
wav_file = "audio.wav"  # Output WAV file path
convert_mp3_to_wav(mp3_file, wav_file)

# Recognize speech from the WAV file
recognizer = sr.Recognizer()

with sr.AudioFile(wav_file) as source:
    print("Processing audio...")
    audio_data = recognizer.record(source)  # Read the entire audio file
    
try:
    # Recognize speech using Google's Web Speech API
    text = recognizer.recognize_google(audio_data)
    print("Recognized Text:")
    print(text)
except sr.UnknownValueError:
    print("Speech Recognition could not understand the audio.")
except sr.RequestError as e:
    print(f"Could not request results from Google Speech Recognition service; {e}")
