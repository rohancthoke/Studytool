import speech_recognition as sr

# Create a recognizer instance
r = sr.Recognizer()

# Define the audio file path
audio_file = "./output_audio.wav"

# Use a language model for improved accuracy (optional)
# Replace "en-US" with the appropriate language code
language_model = sr.AudioFile(audio_file)
with language_model as source:
    audio = r.record(source)
    text = r.recognize_google(audio, language="en-US")

# Print the transcribed text
print(text)
