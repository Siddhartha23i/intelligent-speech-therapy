from modules.audio_preprocessing import preprocess_audio

input_audio = "data/raw_audio/reference/sample.wav"
output_audio = "data/processed_audio/sample_clean.wav"

preprocess_audio(input_audio, output_audio)

print("Audio preprocessing successful!")
