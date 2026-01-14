import json
import wave
from vosk import Model, KaldiRecognizer

def align_words(audio_path, model_path="models/vosk-en"):
    wf = wave.open(audio_path, "rb")

    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    results = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))

    results.append(json.loads(rec.FinalResult()))
    return results
