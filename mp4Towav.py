from pydub import AudioSegment

def convert_mp4_to_wav(input_file, output_file):
    # Load audio file using PyDub
    audio = AudioSegment.from_file(input_file, format="mp4")

    # Write the audio to a WAV file
    audio.export(output_file, format="wav")

if __name__ == "__main__":
    input_file_path = "./in/A.mp4"  # Change this to your input .mp4 file
    output_file_path = "./out/output_audio.wav"  # Change this to your desired output .wav file

    convert_mp4_to_wav(input_file_path, output_file_path)
