from modules.vosk_alignment import align_words

audio = "data/align_audio/sample.wav"

results = align_words(audio)

print("\nWORD TIMESTAMPS:")
for r in results:
    if "result" in r:
        for w in r["result"]:
            print(w["word"], w["start"], w["end"])
