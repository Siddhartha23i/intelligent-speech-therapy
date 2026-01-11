<<<<<<< HEAD
"""
Pronunciation Scoring Module for Speech Therapy Platform

This module handles pronunciation analysis and scoring:
- Loading/creating reference phoneme embeddings
- Scoring individual phonemes
- Identifying pronunciation errors
- Detecting error types
"""

import numpy as np
import pickle
import os
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple
import json


def load_or_create_reference_embeddings(embeddings_path='models/reference_embeddings.pkl'):
    """
    Load existing reference embeddings or create synthetic ones.
    
    Args:
        embeddings_path: Path to save/load embeddings pickle file
    
    Returns:
        dict: Dictionary mapping phonemes to reference feature vectors
    """
    # Check if embeddings file exists
    if os.path.exists(embeddings_path):
        try:
            with open(embeddings_path, 'rb') as f:
                embeddings = pickle.load(f)
            return embeddings
        except Exception as e:
            print(f"Error loading embeddings: {e}. Creating new ones...")
    
    # Create synthetic reference embeddings based on phonetic properties
    # These are approximations based on acoustic phonetics principles
    reference_embeddings = {
        # Dental fricatives
        'TH': np.array([0.5, 0.3, -0.2, 0.1, 0.0, -0.1, 0.2, 0.1, -0.3, 0.0, 0.1, -0.2, 0.3]),
        'DH': np.array([0.5, 0.4, -0.2, 0.2, 0.1, -0.1, 0.2, 0.2, -0.3, 0.1, 0.1, -0.2, 0.3]),
        
        # Alveolar approximants
        'R': np.array([0.3, 0.2, 0.4, 0.3, -0.1, 0.0, 0.1, 0.3, 0.2, 0.1, -0.2, 0.0, 0.2]),
        'L': np.array([0.2, 0.3, 0.3, 0.2, 0.0, 0.1, 0.0, 0.2, 0.3, 0.2, -0.1, 0.1, 0.1]),
        
        # Labiodental fricatives
        'F': np.array([0.6, 0.2, -0.3, 0.0, -0.2, 0.1, 0.3, 0.0, -0.4, -0.1, 0.2, -0.3, 0.4]),
        'V': np.array([0.6, 0.3, -0.3, 0.1, -0.1, 0.1, 0.3, 0.1, -0.4, 0.0, 0.2, -0.3, 0.4]),
        
        # Labio-velar
        'W': np.array([0.2, 0.4, 0.3, 0.1, 0.0, 0.0, 0.1, 0.2, 0.1, 0.0, -0.2, 0.1, 0.0]),
        
        # Alveolar fricatives
        'S': np.array([0.7, 0.1, -0.4, -0.1, -0.3, 0.2, 0.4, -0.1, -0.5, -0.2, 0.3, -0.4, 0.5]),
        'Z': np.array([0.7, 0.2, -0.4, 0.0, -0.2, 0.2, 0.4, 0.0, -0.5, -0.1, 0.3, -0.4, 0.5]),
        
        # Postalveolar fricatives
        'SH': np.array([0.6, 0.0, -0.3, -0.2, -0.4, 0.3, 0.5, -0.2, -0.4, -0.3, 0.4, -0.3, 0.4]),
        'ZH': np.array([0.6, 0.1, -0.3, -0.1, -0.3, 0.3, 0.5, -0.1, -0.4, -0.2, 0.4, -0.3, 0.4]),
        
        # Affricates
        'CH': np.array([0.5, 0.0, -0.2, -0.1, -0.3, 0.2, 0.4, -0.1, -0.3, -0.2, 0.3, -0.2, 0.3]),
        'JH': np.array([0.5, 0.1, -0.2, 0.0, -0.2, 0.2, 0.4, 0.0, -0.3, -0.1, 0.3, -0.2, 0.3]),
        
        # Plosives
        'P': np.array([0.4, -0.2, 0.1, -0.3, 0.2, 0.0, 0.2, -0.2, 0.0, -0.3, 0.1, 0.1, 0.2]),
        'B': np.array([0.4, -0.1, 0.1, -0.2, 0.3, 0.0, 0.2, -0.1, 0.0, -0.2, 0.1, 0.1, 0.2]),
        'T': np.array([0.5, -0.3, 0.0, -0.4, 0.1, 0.1, 0.3, -0.3, -0.1, -0.4, 0.2, 0.0, 0.3]),
        'D': np.array([0.5, -0.2, 0.0, -0.3, 0.2, 0.1, 0.3, -0.2, -0.1, -0.3, 0.2, 0.0, 0.3]),
        'K': np.array([0.4, -0.4, -0.1, -0.5, 0.0, 0.2, 0.2, -0.4, -0.2, -0.5, 0.3, -0.1, 0.2]),
        'G': np.array([0.4, -0.3, -0.1, -0.4, 0.1, 0.2, 0.2, -0.3, -0.2, -0.4, 0.3, -0.1, 0.2]),
        
        # Nasals
        'M': np.array([0.3, 0.5, 0.2, 0.4, 0.3, -0.1, 0.0, 0.4, 0.3, 0.3, -0.2, 0.2, 0.1]),
        'N': np.array([0.3, 0.4, 0.1, 0.3, 0.2, 0.0, 0.1, 0.3, 0.2, 0.2, -0.1, 0.1, 0.2]),
        'NG': np.array([0.3, 0.3, 0.0, 0.2, 0.1, 0.1, 0.0, 0.2, 0.1, 0.1, 0.0, 0.0, 0.1]),
        
        # Approximants/Glides
        'Y': np.array([0.2, 0.3, 0.4, 0.2, 0.1, 0.0, 0.0, 0.2, 0.3, 0.1, -0.1, 0.1, 0.0]),
        'HH': np.array([0.3, -0.1, -0.1, -0.2, -0.2, 0.1, 0.2, -0.1, -0.2, -0.2, 0.1, -0.1, 0.2]),
        
        # Vowels (simplified - g2p_en uses specific vowel codes)
        'AA': np.array([0.1, 0.6, 0.3, 0.4, 0.2, -0.2, -0.1, 0.5, 0.4, 0.2, -0.3, 0.3, 0.0]),
        'AE': np.array([0.1, 0.5, 0.2, 0.3, 0.1, -0.1, 0.0, 0.4, 0.3, 0.1, -0.2, 0.2, 0.1]),
        'AH': np.array([0.0, 0.4, 0.1, 0.2, 0.0, 0.0, 0.0, 0.3, 0.2, 0.0, -0.1, 0.1, 0.0]),
        'AO': np.array([0.1, 0.5, 0.3, 0.3, 0.2, -0.2, -0.1, 0.4, 0.4, 0.2, -0.3, 0.2, 0.0]),
        'AW': np.array([0.1, 0.5, 0.3, 0.3, 0.1, -0.1, 0.0, 0.4, 0.3, 0.1, -0.2, 0.2, 0.1]),
        'AY': np.array([0.1, 0.4, 0.3, 0.2, 0.1, 0.0, 0.0, 0.3, 0.3, 0.1, -0.1, 0.2, 0.1]),
        'EH': np.array([0.0, 0.4, 0.2, 0.2, 0.1, -0.1, 0.0, 0.3, 0.2, 0.1, -0.1, 0.1, 0.1]),
        'ER': np.array([0.2, 0.3, 0.3, 0.2, 0.0, 0.0, 0.1, 0.2, 0.3, 0.1, -0.1, 0.1, 0.1]),
        'EY': np.array([0.0, 0.3, 0.3, 0.2, 0.1, 0.0, 0.0, 0.2, 0.2, 0.1, 0.0, 0.1, 0.1]),
        'IH': np.array([0.0, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0, 0.2, 0.1, 0.0, 0.0, 0.1, 0.0]),
        'IY': np.array([0.0, 0.2, 0.3, 0.1, 0.1, 0.1, 0.0, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1]),
        'OW': np.array([0.1, 0.4, 0.4, 0.3, 0.2, -0.1, 0.0, 0.3, 0.4, 0.2, -0.2, 0.2, 0.1]),
        'OY': np.array([0.1, 0.4, 0.3, 0.2, 0.1, -0.1, 0.0, 0.3, 0.3, 0.1, -0.1, 0.2, 0.1]),
        'UH': np.array([0.1, 0.3, 0.2, 0.2, 0.1, 0.0, 0.0, 0.2, 0.2, 0.1, -0.1, 0.1, 0.0]),
        'UW': np.array([0.1, 0.2, 0.4, 0.2, 0.2, 0.0, 0.0, 0.1, 0.3, 0.2, 0.0, 0.1, 0.1]),
    }
    
    # Save embeddings
    os.makedirs(os.path.dirname(embeddings_path), exist_ok=True)
    try:
        with open(embeddings_path, 'wb') as f:
            pickle.dump(reference_embeddings, f)
    except Exception as e:
        print(f"Warning: Could not save reference embeddings: {e}")
    
    return reference_embeddings


def score_phoneme(user_embedding, reference_embedding):
    """
    Score a single phoneme pronunciation.
    
    Args:
        user_embedding: User's phoneme feature vector
        reference_embedding: Reference phoneme feature vector
    
    Returns:
        float: Score from 0-100
    """
    # Reshape for sklearn
    user_emb = user_embedding.reshape(1, -1)
    ref_emb = reference_embedding.reshape(1, -1)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(user_emb, ref_emb)[0][0]
    
    # Convert to 0-100 scale
    # Cosine similarity ranges from -1 to 1, we map this to 0-100
    score = (similarity + 1) / 2 * 100
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    return score


def score_pronunciation(alignments, reference_embeddings):
    """
    Score overall pronunciation based on phoneme alignments.
    
    Args:
        alignments: List of phoneme alignment dictionaries with features
        reference_embeddings: Dictionary of reference embeddings
    
    Returns:
        dict: Comprehensive scoring results
    """
    phoneme_scores = []
    weak_phonemes = []
    mistakes = []
    
    for alignment in alignments:
        phoneme = alignment['phoneme']
        user_features = alignment.get('features')
        
        if user_features is None:
            continue
        
        # Get reference embedding (use a default if phoneme not in references)
        ref_embedding = reference_embeddings.get(
            phoneme,
            np.zeros(13)  # Default zero vector for unknown phonemes
        )
        
        # Score the phoneme
        score = score_phoneme(user_features, ref_embedding)
        
        phoneme_data = {
            'phoneme': phoneme,
            'score': score,
            'start_time': alignment['start_time'],
            'end_time': alignment['end_time']
        }
        
        phoneme_scores.append(phoneme_data)
        
        # Identify weak phonemes (score < 70)
        if score < 70:
            weak_phonemes.append(phoneme)
        
        # Identify mistakes (score < 50)
        if score < 50:
            mistakes.append(phoneme_data)
    
    # Calculate overall score
    if phoneme_scores:
        overall_score = np.mean([p['score'] for p in phoneme_scores])
    else:
        overall_score = 0
    
    # Calculate fluency score (based on score variance - lower variance = more fluent)
    if len(phoneme_scores) > 1:
        score_variance = np.var([p['score'] for p in phoneme_scores])
        fluency_score = max(0, 100 - score_variance)
    else:
        fluency_score = overall_score
    
    return {
        'overall_score': round(overall_score, 1),
        'phoneme_scores': phoneme_scores,
        'weak_phonemes': list(set(weak_phonemes)),  # Remove duplicates
        'mistakes': mistakes,
        'fluency_score': round(fluency_score, 1),
        'total_phonemes': len(phoneme_scores)
    }


def detect_error_type(user_embedding, expected_phoneme, reference_embeddings):
    """
    Detect the type of pronunciation error.
    
    Args:
        user_embedding: User's phoneme feature vector
        expected_phoneme: Expected phoneme
        reference_embeddings: All reference embeddings
    
    Returns:
        str: Error type description
    """
    # Score against expected phoneme
    expected_score = score_phoneme(
        user_embedding,
        reference_embeddings.get(expected_phoneme, np.zeros(13))
    )
    
    # Score against all phonemes to find closest match
    best_match = expected_phoneme
    best_score = expected_score
    
    for phoneme, ref_emb in reference_embeddings.items():
        score = score_phoneme(user_embedding, ref_emb)
        if score > best_score:
            best_score = score
            best_match = phoneme
    
    # Classify error
    if expected_score >= 70:
        return "correct"
    elif best_match != expected_phoneme:
        return f"substitution: {expected_phoneme} → {best_match}"
    elif expected_score < 50:
        return "weak"
    else:
        return "imprecise"


def get_phoneme_feedback(score):
    """
    Get descriptive feedback for a phoneme score.
    
    Args:
        score: Phoneme score (0-100)
    
    Returns:
        str: Feedback description
    """
    if score >= 90:
        return "Excellent!"
    elif score >= 80:
        return "Very good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Acceptable"
    elif score >= 50:
        return "Needs practice"
    else:
        return "Needs significant improvement"
=======
"""
Pronunciation Scoring Module for Speech Therapy Platform

This module handles pronunciation analysis and scoring:
- Loading/creating reference phoneme embeddings
- Scoring individual phonemes
- Identifying pronunciation errors
- Detecting error types
"""

import numpy as np
import pickle
import os
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple
import json


def load_or_create_reference_embeddings(embeddings_path='models/reference_embeddings.pkl'):
    """
    Load existing reference embeddings or create synthetic ones.
    
    Args:
        embeddings_path: Path to save/load embeddings pickle file
    
    Returns:
        dict: Dictionary mapping phonemes to reference feature vectors
    """
    # Check if embeddings file exists
    if os.path.exists(embeddings_path):
        try:
            with open(embeddings_path, 'rb') as f:
                embeddings = pickle.load(f)
            return embeddings
        except Exception as e:
            print(f"Error loading embeddings: {e}. Creating new ones...")
    
    # Create synthetic reference embeddings based on phonetic properties
    # These are approximations based on acoustic phonetics principles
    reference_embeddings = {
        # Dental fricatives
        'TH': np.array([0.5, 0.3, -0.2, 0.1, 0.0, -0.1, 0.2, 0.1, -0.3, 0.0, 0.1, -0.2, 0.3]),
        'DH': np.array([0.5, 0.4, -0.2, 0.2, 0.1, -0.1, 0.2, 0.2, -0.3, 0.1, 0.1, -0.2, 0.3]),
        
        # Alveolar approximants
        'R': np.array([0.3, 0.2, 0.4, 0.3, -0.1, 0.0, 0.1, 0.3, 0.2, 0.1, -0.2, 0.0, 0.2]),
        'L': np.array([0.2, 0.3, 0.3, 0.2, 0.0, 0.1, 0.0, 0.2, 0.3, 0.2, -0.1, 0.1, 0.1]),
        
        # Labiodental fricatives
        'F': np.array([0.6, 0.2, -0.3, 0.0, -0.2, 0.1, 0.3, 0.0, -0.4, -0.1, 0.2, -0.3, 0.4]),
        'V': np.array([0.6, 0.3, -0.3, 0.1, -0.1, 0.1, 0.3, 0.1, -0.4, 0.0, 0.2, -0.3, 0.4]),
        
        # Labio-velar
        'W': np.array([0.2, 0.4, 0.3, 0.1, 0.0, 0.0, 0.1, 0.2, 0.1, 0.0, -0.2, 0.1, 0.0]),
        
        # Alveolar fricatives
        'S': np.array([0.7, 0.1, -0.4, -0.1, -0.3, 0.2, 0.4, -0.1, -0.5, -0.2, 0.3, -0.4, 0.5]),
        'Z': np.array([0.7, 0.2, -0.4, 0.0, -0.2, 0.2, 0.4, 0.0, -0.5, -0.1, 0.3, -0.4, 0.5]),
        
        # Postalveolar fricatives
        'SH': np.array([0.6, 0.0, -0.3, -0.2, -0.4, 0.3, 0.5, -0.2, -0.4, -0.3, 0.4, -0.3, 0.4]),
        'ZH': np.array([0.6, 0.1, -0.3, -0.1, -0.3, 0.3, 0.5, -0.1, -0.4, -0.2, 0.4, -0.3, 0.4]),
        
        # Affricates
        'CH': np.array([0.5, 0.0, -0.2, -0.1, -0.3, 0.2, 0.4, -0.1, -0.3, -0.2, 0.3, -0.2, 0.3]),
        'JH': np.array([0.5, 0.1, -0.2, 0.0, -0.2, 0.2, 0.4, 0.0, -0.3, -0.1, 0.3, -0.2, 0.3]),
        
        # Plosives
        'P': np.array([0.4, -0.2, 0.1, -0.3, 0.2, 0.0, 0.2, -0.2, 0.0, -0.3, 0.1, 0.1, 0.2]),
        'B': np.array([0.4, -0.1, 0.1, -0.2, 0.3, 0.0, 0.2, -0.1, 0.0, -0.2, 0.1, 0.1, 0.2]),
        'T': np.array([0.5, -0.3, 0.0, -0.4, 0.1, 0.1, 0.3, -0.3, -0.1, -0.4, 0.2, 0.0, 0.3]),
        'D': np.array([0.5, -0.2, 0.0, -0.3, 0.2, 0.1, 0.3, -0.2, -0.1, -0.3, 0.2, 0.0, 0.3]),
        'K': np.array([0.4, -0.4, -0.1, -0.5, 0.0, 0.2, 0.2, -0.4, -0.2, -0.5, 0.3, -0.1, 0.2]),
        'G': np.array([0.4, -0.3, -0.1, -0.4, 0.1, 0.2, 0.2, -0.3, -0.2, -0.4, 0.3, -0.1, 0.2]),
        
        # Nasals
        'M': np.array([0.3, 0.5, 0.2, 0.4, 0.3, -0.1, 0.0, 0.4, 0.3, 0.3, -0.2, 0.2, 0.1]),
        'N': np.array([0.3, 0.4, 0.1, 0.3, 0.2, 0.0, 0.1, 0.3, 0.2, 0.2, -0.1, 0.1, 0.2]),
        'NG': np.array([0.3, 0.3, 0.0, 0.2, 0.1, 0.1, 0.0, 0.2, 0.1, 0.1, 0.0, 0.0, 0.1]),
        
        # Approximants/Glides
        'Y': np.array([0.2, 0.3, 0.4, 0.2, 0.1, 0.0, 0.0, 0.2, 0.3, 0.1, -0.1, 0.1, 0.0]),
        'HH': np.array([0.3, -0.1, -0.1, -0.2, -0.2, 0.1, 0.2, -0.1, -0.2, -0.2, 0.1, -0.1, 0.2]),
        
        # Vowels (simplified - g2p_en uses specific vowel codes)
        'AA': np.array([0.1, 0.6, 0.3, 0.4, 0.2, -0.2, -0.1, 0.5, 0.4, 0.2, -0.3, 0.3, 0.0]),
        'AE': np.array([0.1, 0.5, 0.2, 0.3, 0.1, -0.1, 0.0, 0.4, 0.3, 0.1, -0.2, 0.2, 0.1]),
        'AH': np.array([0.0, 0.4, 0.1, 0.2, 0.0, 0.0, 0.0, 0.3, 0.2, 0.0, -0.1, 0.1, 0.0]),
        'AO': np.array([0.1, 0.5, 0.3, 0.3, 0.2, -0.2, -0.1, 0.4, 0.4, 0.2, -0.3, 0.2, 0.0]),
        'AW': np.array([0.1, 0.5, 0.3, 0.3, 0.1, -0.1, 0.0, 0.4, 0.3, 0.1, -0.2, 0.2, 0.1]),
        'AY': np.array([0.1, 0.4, 0.3, 0.2, 0.1, 0.0, 0.0, 0.3, 0.3, 0.1, -0.1, 0.2, 0.1]),
        'EH': np.array([0.0, 0.4, 0.2, 0.2, 0.1, -0.1, 0.0, 0.3, 0.2, 0.1, -0.1, 0.1, 0.1]),
        'ER': np.array([0.2, 0.3, 0.3, 0.2, 0.0, 0.0, 0.1, 0.2, 0.3, 0.1, -0.1, 0.1, 0.1]),
        'EY': np.array([0.0, 0.3, 0.3, 0.2, 0.1, 0.0, 0.0, 0.2, 0.2, 0.1, 0.0, 0.1, 0.1]),
        'IH': np.array([0.0, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0, 0.2, 0.1, 0.0, 0.0, 0.1, 0.0]),
        'IY': np.array([0.0, 0.2, 0.3, 0.1, 0.1, 0.1, 0.0, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1]),
        'OW': np.array([0.1, 0.4, 0.4, 0.3, 0.2, -0.1, 0.0, 0.3, 0.4, 0.2, -0.2, 0.2, 0.1]),
        'OY': np.array([0.1, 0.4, 0.3, 0.2, 0.1, -0.1, 0.0, 0.3, 0.3, 0.1, -0.1, 0.2, 0.1]),
        'UH': np.array([0.1, 0.3, 0.2, 0.2, 0.1, 0.0, 0.0, 0.2, 0.2, 0.1, -0.1, 0.1, 0.0]),
        'UW': np.array([0.1, 0.2, 0.4, 0.2, 0.2, 0.0, 0.0, 0.1, 0.3, 0.2, 0.0, 0.1, 0.1]),
    }
    
    # Save embeddings
    os.makedirs(os.path.dirname(embeddings_path), exist_ok=True)
    try:
        with open(embeddings_path, 'wb') as f:
            pickle.dump(reference_embeddings, f)
    except Exception as e:
        print(f"Warning: Could not save reference embeddings: {e}")
    
    return reference_embeddings


def score_phoneme(user_embedding, reference_embedding):
    """
    Score a single phoneme pronunciation.
    
    Args:
        user_embedding: User's phoneme feature vector
        reference_embedding: Reference phoneme feature vector
    
    Returns:
        float: Score from 0-100
    """
    # Reshape for sklearn
    user_emb = user_embedding.reshape(1, -1)
    ref_emb = reference_embedding.reshape(1, -1)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(user_emb, ref_emb)[0][0]
    
    # Convert to 0-100 scale
    # Cosine similarity ranges from -1 to 1, we map this to 0-100
    score = (similarity + 1) / 2 * 100
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    return score


def score_pronunciation(alignments, reference_embeddings):
    """
    Score overall pronunciation based on phoneme alignments.
    
    Args:
        alignments: List of phoneme alignment dictionaries with features
        reference_embeddings: Dictionary of reference embeddings
    
    Returns:
        dict: Comprehensive scoring results
    """
    phoneme_scores = []
    weak_phonemes = []
    mistakes = []
    
    for alignment in alignments:
        phoneme = alignment['phoneme']
        user_features = alignment.get('features')
        
        if user_features is None:
            continue
        
        # Get reference embedding (use a default if phoneme not in references)
        ref_embedding = reference_embeddings.get(
            phoneme,
            np.zeros(13)  # Default zero vector for unknown phonemes
        )
        
        # Score the phoneme
        score = score_phoneme(user_features, ref_embedding)
        
        phoneme_data = {
            'phoneme': phoneme,
            'score': score,
            'start_time': alignment['start_time'],
            'end_time': alignment['end_time']
        }
        
        phoneme_scores.append(phoneme_data)
        
        # Identify weak phonemes (score < 70)
        if score < 70:
            weak_phonemes.append(phoneme)
        
        # Identify mistakes (score < 50)
        if score < 50:
            mistakes.append(phoneme_data)
    
    # Calculate overall score
    if phoneme_scores:
        overall_score = np.mean([p['score'] for p in phoneme_scores])
    else:
        overall_score = 0
    
    # Calculate fluency score (based on score variance - lower variance = more fluent)
    if len(phoneme_scores) > 1:
        score_variance = np.var([p['score'] for p in phoneme_scores])
        fluency_score = max(0, 100 - score_variance)
    else:
        fluency_score = overall_score
    
    return {
        'overall_score': round(overall_score, 1),
        'phoneme_scores': phoneme_scores,
        'weak_phonemes': list(set(weak_phonemes)),  # Remove duplicates
        'mistakes': mistakes,
        'fluency_score': round(fluency_score, 1),
        'total_phonemes': len(phoneme_scores)
    }


def detect_error_type(user_embedding, expected_phoneme, reference_embeddings):
    """
    Detect the type of pronunciation error.
    
    Args:
        user_embedding: User's phoneme feature vector
        expected_phoneme: Expected phoneme
        reference_embeddings: All reference embeddings
    
    Returns:
        str: Error type description
    """
    # Score against expected phoneme
    expected_score = score_phoneme(
        user_embedding,
        reference_embeddings.get(expected_phoneme, np.zeros(13))
    )
    
    # Score against all phonemes to find closest match
    best_match = expected_phoneme
    best_score = expected_score
    
    for phoneme, ref_emb in reference_embeddings.items():
        score = score_phoneme(user_embedding, ref_emb)
        if score > best_score:
            best_score = score
            best_match = phoneme
    
    # Classify error
    if expected_score >= 70:
        return "correct"
    elif best_match != expected_phoneme:
        return f"substitution: {expected_phoneme} → {best_match}"
    elif expected_score < 50:
        return "weak"
    else:
        return "imprecise"


def get_phoneme_feedback(score):
    """
    Get descriptive feedback for a phoneme score.
    
    Args:
        score: Phoneme score (0-100)
    
    Returns:
        str: Feedback description
    """
    if score >= 90:
        return "Excellent!"
    elif score >= 80:
        return "Very good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Acceptable"
    elif score >= 50:
        return "Needs practice"
    else:
        return "Needs significant improvement"
>>>>>>> 91fcca26e074a943dc9c8fb178dacc68158b4847
