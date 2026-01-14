import subprocess
import os

def run_forced_alignment(audio_dir, text_dir, output_dir):
    """
    Runs Montreal Forced Aligner
    audio_dir: folder containing wav files
    text_dir: folder containing txt transcripts
    output_dir: output alignment folder
    """

    os.makedirs(output_dir, exist_ok=True)

    command = [
        "mfa",
        "align",
        audio_dir,
        text_dir,
        "english_us_arpa",
        output_dir,
        "--clean"
    ]

    subprocess.run(command, check=True)
