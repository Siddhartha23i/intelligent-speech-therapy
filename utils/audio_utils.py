
"""
Audio Utility Functions for Speech Therapy Platform

Helper functions for audio file operations.
"""

import numpy as np
import soundfile as sf
import base64
import io
import os
from pydub import AudioSegment


def save_audio(audio_bytes, filename):
    """
    Save audio bytes to a file.
    
    Args:
        audio_bytes: Audio data as bytes
        filename: Destination filepath
    
    Returns:
        str: Saved file path
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'wb') as f:
        f.write(audio_bytes)
    
    return filename


def load_audio(filepath, sr=16000):
    """
    Load audio from file.
    
    Args:
        filepath: Path to audio file
        sr: Target sample rate
    
    Returns:
        tuple: (audio_array, sample_rate)
    """
    import librosa
    audio_array, sample_rate = librosa.load(filepath, sr=sr, mono=True)
    return audio_array, sample_rate


def audio_to_base64(audio_array, sr=16000):
    """
    Convert audio array to base64 string for web playback.
    
    Args:
        audio_array: Audio data as numpy array
        sr: Sample rate
    
    Returns:
        str: Base64 encoded audio string
    """
    # Convert to bytes
    buffer = io.BytesIO()
    sf.write(buffer, audio_array, sr, format='WAV')
    buffer.seek(0)
    
    # Encode to base64
    audio_base64 = base64.b64encode(buffer.read()).decode()
    
    return f"data:audio/wav;base64,{audio_base64}"


def calculate_audio_duration(audio_array, sr):
    """
    Calculate duration of audio in seconds.
    
    Args:
        audio_array: Audio data as numpy array
        sr: Sample rate
    
    Returns:
        float: Duration in seconds
    """
    return len(audio_array) / sr


def convert_audio_format(input_path, output_path, output_format='wav'):
    """
    Convert audio file to different format.
    
    Args:
        input_path: Input file path
        output_path: Output file path
        output_format: Desired output format
    
    Returns:
        str: Output file path
    """
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format=output_format)
    return output_path


def normalize_audio_volume(audio_array, target_level=-20.0):
    """
    Normalize audio volume to target level in dB.
    
    Args:
        audio_array: Audio data as numpy array
        target_level: Target volume level in dB
    
    Returns:
        numpy.ndarray: Normalized audio array
    """
    # Calculate current RMS
    rms = np.sqrt(np.mean(audio_array**2))
    
    if rms == 0:
        return audio_array
    
    # Calculate gain needed
    current_db = 20 * np.log10(rms)
    gain_db = target_level - current_db
    gain = 10 ** (gain_db / 20)
    
    # Apply gain
    normalized = audio_array * gain
    
    # Clip to prevent distortion
    normalized = np.clip(normalized, -1.0, 1.0)
    
    return normalized


def trim_silence(audio_array, sr, threshold_db=-40):
    """
    Trim silence from audio.
    
    Args:
        audio_array: Audio data as numpy array
        sr: Sample rate
        threshold_db: Silence threshold in dB
    
    Returns:
        tuple: (trimmed_audio, (start_sample, end_sample))
    """
    import librosa
    
    trimmed, indices = librosa.effects.trim(
        audio_array,
        top_db=-threshold_db
    )
    
    return trimmed, indices


def get_audio_info(filepath):
    """
    Get information about an audio file.
    
    Args:
        filepath: Path to audio file
    
    Returns:
        dict: Audio file information
    """
    audio = AudioSegment.from_file(filepath)
    
    return {
        'duration_seconds': len(audio) / 1000.0,
        'channels': audio.channels,
        'sample_rate': audio.frame_rate,
        'sample_width': audio.sample_width,
        'file_size_mb': os.path.getsize(filepath) / (1024 * 1024)
    }
