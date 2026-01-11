 
"""
Text Processing Utility Functions for Speech Therapy Platform

Helper functions for text manipulation and comparison.
"""

import re
from difflib import SequenceMatcher
import json
import os


def normalize_text(text):
    """
    Normalize text by converting to lowercase and removing punctuation.
    
    Args:
        text: Input text string
    
    Returns:
        str: Normalized text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation (keep apostrophes)
    text = re.sub(r"[^\w\s']", '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


def compare_sentences(expected, actual):
    """
    Compare two sentences and calculate similarity.
    
    Args:
        expected: Expected sentence
        actual: Actual transcribed sentence
    
    Returns:
        dict: Comparison results
    """
    # Normalize both sentences
    expected_norm = normalize_text(expected)
    actual_norm = normalize_text(actual)
    
    # Calculate similarity ratio
    similarity = SequenceMatcher(None, expected_norm, actual_norm).ratio()
    
    # Split into words
    expected_words = expected_norm.split()
    actual_words = actual_norm.split()
    
    # Find differences
    differences = []
    for i, (exp, act) in enumerate(zip(expected_words, actual_words)):
        if exp != act:
            differences.append({
                'position': i,
                'expected': exp,
                'actual': act
            })
    
    # Handle length differences
    if len(expected_words) != len(actual_words):
        length_diff = abs(len(expected_words) - len(actual_words))
    else:
        length_diff = 0
    
    return {
        'similarity': similarity * 100,  # Convert to percentage
        'exact_match': expected_norm == actual_norm,
        'differences': differences,
        'length_difference': length_diff,
        'expected_word_count': len(expected_words),
        'actual_word_count': len(actual_words)
    }


def highlight_differences(expected, actual):
    """
    Create a highlighted version showing differences.
    
    Args:
        expected: Expected sentence
        actual: Actual sentence
    
    Returns:
        str: Markdown formatted string with highlighted differences
    """
    expected_words = normalize_text(expected).split()
    actual_words = normalize_text(actual).split()
    
    highlighted = []
    
    max_len = max(len(expected_words), len(actual_words))
    
    for i in range(max_len):
        if i < len(actual_words):
            actual_word = actual_words[i]
            
            if i < len(expected_words):
                expected_word = expected_words[i]
                
                if actual_word == expected_word:
                    # Correct word
                    highlighted.append(actual_word)
                else:
                    # Different word - highlight in red
                    highlighted.append(f"**~~{actual_word}~~** (*{expected_word}*)")
            else:
                # Extra word
                highlighted.append(f"**+{actual_word}**")
    
    # Handle missing words
    if len(expected_words) > len(actual_words):
        for i in range(len(actual_words), len(expected_words)):
            highlighted.append(f"*-{expected_words[i]}*")
    
    return ' '.join(highlighted)


def phoneme_to_readable(phoneme):
    """
    Convert phoneme code to readable description.
    
    Args:
        phoneme: Phoneme code (e.g., 'TH', 'R')
    
    Returns:
        str: Readable description
    """
    # Load phoneme mapping
    phoneme_file = 'data/phoneme_mapping.json'
    
    if os.path.exists(phoneme_file):
        with open(phoneme_file, 'r') as f:
            data = json.load(f)
            phoneme_info = data.get('phoneme_info', {})
            
            if phoneme in phoneme_info:
                info = phoneme_info[phoneme]
                examples = info.get('example_words', [])
                ipa = info.get('ipa', '')
                
                readable = f"{phoneme}"
                if ipa:
                    readable += f" /{ipa}/"
                if examples:
                    readable += f" (as in '{examples[0]}')"
                
                return readable
    
    return phoneme


def extract_keywords(sentence):
    """
    Extract keywords from a sentence.
    
    Args:
        sentence: Input sentence
    
    Returns:
        list: List of keywords
    """
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can'
    }
    
    # Normalize and split
    words = normalize_text(sentence).split()
    
    # Filter out stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return keywords


def split_into_chunks(text, max_chunk_length=100):
    """
    Split long text into smaller chunks.
    
    Args:
        text: Input text
        max_chunk_length: Maximum characters per chunk
    
    Returns:
        list: List of text chunks
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for space
        
        if current_length + word_length > max_chunk_length and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def calculate_reading_time(text, words_per_minute=150):
    """
    Estimate reading time for text.
    
    Args:
        text: Input text
        words_per_minute: Average reading speed
    
    Returns:
        float: Estimated reading time in minutes
    """
    word_count = len(text.split())
    reading_time = word_count / words_per_minute
    return reading_time


def is_valid_sentence(text):
    """
    Check if text is a valid sentence.
    
    Args:
        text: Input text
    
    Returns:
        bool: True if valid sentence
    """
    if not text or len(text.strip()) == 0:
        return False
    
    # Should have at least one word
    words = text.split()
    if len(words) == 0:
        return False
    
    # Should not be too long
    if len(text) > 500:
        return False
    
    return True
