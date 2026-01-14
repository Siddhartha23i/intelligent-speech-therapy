import os
import parselmouth
import soundfile as sf

def slice_phonemes(audio_path, textgrid_path, output_dir):
    """
    Slice audio into phoneme-level wav files using TextGrid
    """
    os.makedirs(output_dir, exist_ok=True)

    sound = parselmouth.Sound(audio_path)
    tg = parselmouth.read(textgrid_path)

    phone_tier = tg.get_tier_by_name("phones")

    for i, interval in enumerate(phone_tier.intervals):
        label = interval.text.strip()
        if label:
            start = interval.xmin
            end = interval.xmax

            clip = sound.extract_part(start, end, preserve_times=False)
            file_path = os.path.join(output_dir, f"{label}_{i}.wav")

            sf.write(
                file_path,
                clip.values.T,
                int(clip.sampling_frequency)
            )
