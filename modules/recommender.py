<<<<<<< HEAD
"""
Recommendation Module for Speech Therapy Platform

This module recommends practice exercises based on identified weak phonemes:
- Loading sentence banks
- Recommending targeted practice sentences
- Tracking practice history
"""

import os
import random
from typing import List, Dict
from collections import defaultdict


def load_sentence_banks():
    """
    Load all sentence banks from files.
    
    Returns:
        dict: Dictionary mapping phonemes to practice sentences
    """
    sentence_banks = defaultdict(list)
    sentence_banks_dir = 'data/sentence_banks'
    
    if not os.path.exists(sentence_banks_dir):
        return sentence_banks
    
    # Load all text files in sentence_banks directory
    for filename in os.listdir(sentence_banks_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(sentence_banks_dir, filename)
            
            # Determine phoneme from filename
            if filename == 'general_practice.txt':
                phoneme = 'GENERAL'
            else:
                # Extract phoneme from filename like 'phoneme_th.txt'
                phoneme = filename.replace('phoneme_', '').replace('.txt', '').upper()
            
            # Read sentences
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    sentences = [line.strip() for line in f if line.strip()]
                    sentence_banks[phoneme] = sentences
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return dict(sentence_banks)


def get_recommendations(weak_phonemes, num_sentences=5):
    """
    Get recommended practice sentences based on weak phonemes.
    
    Args:
        weak_phonemes: List of phoneme strings that need practice
        num_sentences: Number of sentences to recommend
    
    Returns:
        list: List of recommended practice sentences with metadata
    """
    sentence_banks = load_sentence_banks()
    recommendations = []
    
    if not weak_phonemes:
        # No specific weak phonemes, return general practice
        general_sentences = sentence_banks.get('GENERAL', [])
        if general_sentences:
            selected = random.sample(
                general_sentences,
                min(num_sentences, len(general_sentences))
            )
            return [{'sentence': s, 'focus': 'General Practice', 'priority': 'medium'} for s in selected]
        return []
    
    # Prioritize sentences based on weak phonemes
    phoneme_sentences = []
    
    for phoneme in weak_phonemes:
        # Try to find specific sentence bank for this phoneme
        bank = sentence_banks.get(phoneme, [])
        
        if bank:
            # Add sentences from this phoneme's bank
            for sentence in bank:
                phoneme_sentences.append({
                    'sentence': sentence,
                    'focus': f'{phoneme} sound practice',
                    'priority': 'high',
                    'phoneme': phoneme
                })
    
    # If we have enough phoneme-specific sentences, use those
    if phoneme_sentences:
        # Shuffle to mix different phonemes
        random.shuffle(phoneme_sentences)
        recommendations = phoneme_sentences[:num_sentences]
    
    # Fill remaining slots with general practice
    if len(recommendations) < num_sentences:
        general_sentences = sentence_banks.get('GENERAL', [])
        remaining = num_sentences - len(recommendations)
        
        if general_sentences:
            selected_general = random.sample(
                general_sentences,
                min(remaining, len(general_sentences))
            )
            
            for sentence in selected_general:
                recommendations.append({
                    'sentence': sentence,
                    'focus': 'General Practice',
                    'priority': 'medium'
                })
    
    return recommendations


def track_practice_history(user_id, weak_phonemes, db_connection=None):
    """
    Track user's practice history for weak phonemes.
    
    Args:
        user_id: User identifier
        weak_phonemes: List of weak phonemes from this session
        db_connection: Database connection (optional)
    
    Returns:
        None
    """
    # This will be implemented when database module is ready
    # For now, just return
    if db_connection:
        from utils.db_utils import update_weak_phonemes
        update_weak_phonemes(db_connection, user_id, weak_phonemes)


def get_phoneme_priority(phoneme, practice_history=None):
    """
    Determine priority for practicing a specific phoneme.
    
    Args:
        phoneme: Phoneme string
        practice_history: Optional dictionary of phoneme practice history
    
    Returns:
        str: Priority level ('high', 'medium', 'low')
    """
    if practice_history is None:
        return 'medium'
    
    # Check how often this phoneme has been weak
    frequency = practice_history.get(phoneme, 0)
    
    if frequency >= 3:
        return 'high'
    elif frequency >= 1:
        return 'medium'
    else:
        return 'low'


def get_practice_plan(weak_phonemes, current_level='beginner', sessions=5):
    """
    Create a structured practice plan for multiple sessions.
    
    Args:
        weak_phonemes: List of weak phonemes
        current_level: User's current proficiency level
        sessions: Number of practice sessions to plan
    
    Returns:
        list: List of session plans
    """
    sentence_banks = load_sentence_banks()
    practice_plan = []
    
    if not weak_phonemes:
        weak_phonemes = ['GENERAL']
    
    # Distribute phonemes across sessions
    phonemes_per_session = max(1, len(weak_phonemes) // sessions)
    
    for session_num in range(sessions):
        # Select phonemes for this session
        start_idx = session_num * phonemes_per_session
        end_idx = start_idx + phonemes_per_session
        session_phonemes = weak_phonemes[start_idx:end_idx]
        
        if not session_phonemes and weak_phonemes:
            session_phonemes = weak_phonemes[:1]
        
        # Get recommendations for this session
        session_recommendations = get_recommendations(session_phonemes, num_sentences=3)
        
        session_plan = {
            'session_number': session_num + 1,
            'focus_phonemes': session_phonemes,
            'exercises': session_recommendations,
            'estimated_duration': f'{len(session_recommendations) * 2}-{len(session_recommendations) * 3} minutes'
        }
        
        practice_plan.append(session_plan)
    
    return practice_plan


def get_next_practice_sentence(user_history=None):
    """
    Get the next recommended practice sentence based on user history.
    
    Args:
        user_history: User's practice history (optional)
    
    Returns:
        str: Practice sentence
    """
    sentence_banks = load_sentence_banks()
    
    # If no history, return a general sentence
    if not user_history:
        general = sentence_banks.get('GENERAL', [])
        return random.choice(general) if general else "The quick brown fox jumps over the lazy dog."
    
    # Determine weak phonemes from history
    weak_phonemes = user_history.get('weak_phonemes', [])
    
    # Get recommendations
    recommendations = get_recommendations(weak_phonemes, num_sentences=1)
    
    if recommendations:
        return recommendations[0]['sentence']
    
    # Fallback
    general = sentence_banks.get('GENERAL', [])
    return random.choice(general) if general else "Practice makes perfect."
=======
"""
Recommendation Module for Speech Therapy Platform

This module recommends practice exercises based on identified weak phonemes:
- Loading sentence banks
- Recommending targeted practice sentences
- Tracking practice history
"""

import os
import random
from typing import List, Dict
from collections import defaultdict


def load_sentence_banks():
    """
    Load all sentence banks from files.
    
    Returns:
        dict: Dictionary mapping phonemes to practice sentences
    """
    sentence_banks = defaultdict(list)
    sentence_banks_dir = 'data/sentence_banks'
    
    if not os.path.exists(sentence_banks_dir):
        return sentence_banks
    
    # Load all text files in sentence_banks directory
    for filename in os.listdir(sentence_banks_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(sentence_banks_dir, filename)
            
            # Determine phoneme from filename
            if filename == 'general_practice.txt':
                phoneme = 'GENERAL'
            else:
                # Extract phoneme from filename like 'phoneme_th.txt'
                phoneme = filename.replace('phoneme_', '').replace('.txt', '').upper()
            
            # Read sentences
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    sentences = [line.strip() for line in f if line.strip()]
                    sentence_banks[phoneme] = sentences
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return dict(sentence_banks)


def get_recommendations(weak_phonemes, num_sentences=5):
    """
    Get recommended practice sentences based on weak phonemes.
    
    Args:
        weak_phonemes: List of phoneme strings that need practice
        num_sentences: Number of sentences to recommend
    
    Returns:
        list: List of recommended practice sentences with metadata
    """
    sentence_banks = load_sentence_banks()
    recommendations = []
    
    if not weak_phonemes:
        # No specific weak phonemes, return general practice
        general_sentences = sentence_banks.get('GENERAL', [])
        if general_sentences:
            selected = random.sample(
                general_sentences,
                min(num_sentences, len(general_sentences))
            )
            return [{'sentence': s, 'focus': 'General Practice', 'priority': 'medium'} for s in selected]
        return []
    
    # Prioritize sentences based on weak phonemes
    phoneme_sentences = []
    
    for phoneme in weak_phonemes:
        # Try to find specific sentence bank for this phoneme
        bank = sentence_banks.get(phoneme, [])
        
        if bank:
            # Add sentences from this phoneme's bank
            for sentence in bank:
                phoneme_sentences.append({
                    'sentence': sentence,
                    'focus': f'{phoneme} sound practice',
                    'priority': 'high',
                    'phoneme': phoneme
                })
    
    # If we have enough phoneme-specific sentences, use those
    if phoneme_sentences:
        # Shuffle to mix different phonemes
        random.shuffle(phoneme_sentences)
        recommendations = phoneme_sentences[:num_sentences]
    
    # Fill remaining slots with general practice
    if len(recommendations) < num_sentences:
        general_sentences = sentence_banks.get('GENERAL', [])
        remaining = num_sentences - len(recommendations)
        
        if general_sentences:
            selected_general = random.sample(
                general_sentences,
                min(remaining, len(general_sentences))
            )
            
            for sentence in selected_general:
                recommendations.append({
                    'sentence': sentence,
                    'focus': 'General Practice',
                    'priority': 'medium'
                })
    
    return recommendations


def track_practice_history(user_id, weak_phonemes, db_connection=None):
    """
    Track user's practice history for weak phonemes.
    
    Args:
        user_id: User identifier
        weak_phonemes: List of weak phonemes from this session
        db_connection: Database connection (optional)
    
    Returns:
        None
    """
    # This will be implemented when database module is ready
    # For now, just return
    if db_connection:
        from utils.db_utils import update_weak_phonemes
        update_weak_phonemes(db_connection, user_id, weak_phonemes)


def get_phoneme_priority(phoneme, practice_history=None):
    """
    Determine priority for practicing a specific phoneme.
    
    Args:
        phoneme: Phoneme string
        practice_history: Optional dictionary of phoneme practice history
    
    Returns:
        str: Priority level ('high', 'medium', 'low')
    """
    if practice_history is None:
        return 'medium'
    
    # Check how often this phoneme has been weak
    frequency = practice_history.get(phoneme, 0)
    
    if frequency >= 3:
        return 'high'
    elif frequency >= 1:
        return 'medium'
    else:
        return 'low'


def get_practice_plan(weak_phonemes, current_level='beginner', sessions=5):
    """
    Create a structured practice plan for multiple sessions.
    
    Args:
        weak_phonemes: List of weak phonemes
        current_level: User's current proficiency level
        sessions: Number of practice sessions to plan
    
    Returns:
        list: List of session plans
    """
    sentence_banks = load_sentence_banks()
    practice_plan = []
    
    if not weak_phonemes:
        weak_phonemes = ['GENERAL']
    
    # Distribute phonemes across sessions
    phonemes_per_session = max(1, len(weak_phonemes) // sessions)
    
    for session_num in range(sessions):
        # Select phonemes for this session
        start_idx = session_num * phonemes_per_session
        end_idx = start_idx + phonemes_per_session
        session_phonemes = weak_phonemes[start_idx:end_idx]
        
        if not session_phonemes and weak_phonemes:
            session_phonemes = weak_phonemes[:1]
        
        # Get recommendations for this session
        session_recommendations = get_recommendations(session_phonemes, num_sentences=3)
        
        session_plan = {
            'session_number': session_num + 1,
            'focus_phonemes': session_phonemes,
            'exercises': session_recommendations,
            'estimated_duration': f'{len(session_recommendations) * 2}-{len(session_recommendations) * 3} minutes'
        }
        
        practice_plan.append(session_plan)
    
    return practice_plan


def get_next_practice_sentence(user_history=None):
    """
    Get the next recommended practice sentence based on user history.
    
    Args:
        user_history: User's practice history (optional)
    
    Returns:
        str: Practice sentence
    """
    sentence_banks = load_sentence_banks()
    
    # If no history, return a general sentence
    if not user_history:
        general = sentence_banks.get('GENERAL', [])
        return random.choice(general) if general else "The quick brown fox jumps over the lazy dog."
    
    # Determine weak phonemes from history
    weak_phonemes = user_history.get('weak_phonemes', [])
    
    # Get recommendations
    recommendations = get_recommendations(weak_phonemes, num_sentences=1)
    
    if recommendations:
        return recommendations[0]['sentence']
    
    # Fallback
    general = sentence_banks.get('GENERAL', [])
    return random.choice(general) if general else "Practice makes perfect."
>>>>>>> 91fcca26e074a943dc9c8fb178dacc68158b4847
