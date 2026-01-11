
"""
Database Utilities for Speech Therapy Platform (Supabase)

This module handles all database operations using Supabase:
- Session saving
- User history retrieval
- Statistics calculation
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from utils.supabase_client import get_supabase_client


def init_database():
    """
    Initialize database connection (Supabase).
    
    Returns:
        Client: Supabase client instance
    """
    return get_supabase_client()


def ensure_user_exists(client, user_id):
    """
    Ensure user profile exists in database.
    For Supabase, this is handled during signup.
    
    Args:
        client: Supabase client
        user_id: User identifier
    """
    try:
        response = client.from_('user_profiles').select('id').eq('id', user_id).execute()
        return response.data and len(response.data) > 0
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False


def save_session(client, user_id, sentence, transcription, score_data, audio_path=None):
    """
    Save a practice session to Supabase.
    
    Args:
        client: Supabase client
        user_id: User identifier  
        sentence: Expected sentence
        transcription: User's transcription
        score_data: Dictionary with scoring results
        audio_path: Optional path to saved audio file
    
    Returns:
        str: Session ID (UUID)
    """
    try:
        # Insert session
        session_data = {
            'user_id': user_id,
            'sentence': sentence,
            'transcription': transcription,
            'overall_score': score_data.get('overall_score', 0),
            'fluency_score': score_data.get('fluency_score', 0),
            'audio_path': audio_path
        }
        
        session_response = client.from_('sessions').insert(session_data).execute()
        
        if not session_response.data or len(session_response.data) == 0:
            raise Exception("Failed to create session")
        
        session_id = session_response.data[0]['session_id']
        
        # Insert phoneme scores
        phoneme_scores = score_data.get('phoneme_scores', [])
        if phoneme_scores:
            phoneme_data = []
            for phoneme_info in phoneme_scores:
                phoneme_data.append({
                    'session_id': session_id,
                    'phoneme': phoneme_info['phoneme'],
                    'score': phoneme_info['score'],
                    'error_type': None
                })
            
            client.from_('phoneme_scores').insert(phoneme_data).execute()
        
        # Update weak phonemes using stored procedure
        weak_phonemes = score_data.get('weak_phonemes', [])
        for phoneme in weak_phonemes:
            try:
                client.rpc('upsert_weak_phoneme', {
                    'p_user_id': user_id,
                    'p_phoneme': phoneme
                }).execute()
            except Exception as e:
                # Fallback to manual upsert if stored procedure not available
                try:
                    # Try to update existing
                    existing = client.from_('user_weak_phonemes')\
                        .select('*')\
                        .eq('user_id', user_id)\
                        .eq('phoneme', phoneme)\
                        .execute()
                    
                    if existing.data and len(existing.data) > 0:
                        # Update frequency
                        new_frequency = existing.data[0]['frequency'] + 1
                        client.from_('user_weak_phonemes')\
                            .update({'frequency': new_frequency, 'last_occurrence': datetime.now().isoformat()})\
                            .eq('user_id', user_id)\
                            .eq('phoneme', phoneme)\
                            .execute()
                    else:
                        # Insert new
                        client.from_('user_weak_phonemes').insert({
                            'user_id': user_id,
                            'phoneme': phoneme,
                            'frequency': 1,
                            'last_occurrence': datetime.now().isoformat()
                        }).execute()
                except Exception as inner_e:
                    print(f"Error upserting weak phoneme {phoneme}: {inner_e}")
        
        return session_id
        
    except Exception as e:
        print(f"Error saving session: {e}")
        raise e


def get_user_history(client, user_id, limit=50):
    """
    Get user's practice session history from Supabase.
    
    Args:
        client: Supabase client
        user_id: User identifier
        limit: Maximum number of sessions to retrieve
    
    Returns:
        pandas.DataFrame: Session history
    """
    try:
        response = client.from_('sessions')\
            .select('session_id, timestamp, sentence, transcription, overall_score, fluency_score')\
            .eq('user_id', user_id)\
            .order('timestamp', desc=True)\
            .limit(limit)\
            .execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error fetching user history: {e}")
        return pd.DataFrame()


def get_phoneme_statistics(client, user_id):
    """
    Calculate statistics for each phoneme practiced by user.
    
    Args:
        client: Supabase client
        user_id: User identifier
    
    Returns:
        dict: Dictionary with phoneme statistics
    """
    try:
        # Get all phoneme scores for user's sessions
        response = client.from_('phoneme_scores')\
            .select('phoneme, score, sessions!inner(user_id)')\
            .eq('sessions.user_id', user_id)\
            .execute()
        
        if not response.data:
            return {}
        
        # Calculate statistics
        phoneme_data = {}
        for item in response.data:
            phoneme = item['phoneme']
            score = item['score']
            
            if phoneme not in phoneme_data:
                phoneme_data[phoneme] = []
            phoneme_data[phoneme].append(score)
        
        # Aggregate statistics
        stats = {}
        for phoneme, scores in phoneme_data.items():
            stats[phoneme] = {
                'average_score': round(sum(scores) / len(scores), 1),
                'count': len(scores),
                'min_score': round(min(scores), 1),
                'max_score': round(max(scores), 1)
            }
        
        # Sort by average score
        stats = dict(sorted(stats.items(), key=lambda x: x[1]['average_score']))
        
        return stats
        
    except Exception as e:
        print(f"Error fetching phoneme statistics: {e}")
        return {}


def get_weak_phonemes_history(client, user_id):
    """
    Get user's weak phonemes history from Supabase.
    
    Args:
        client: Supabase client
        user_id: User identifier
    
    Returns:
        dict: Dictionary of weak phonemes with frequencies
    """
    try:
        response = client.from_('user_weak_phonemes')\
            .select('phoneme, frequency, last_occurrence')\
            .eq('user_id', user_id)\
            .order('frequency', desc=True)\
            .execute()
        
        if response.data:
            weak_phonemes = {}
            for row in response.data:
                weak_phonemes[row['phoneme']] = {
                    'frequency': row['frequency'],
                    'last_occurrence': row['last_occurrence']
                }
            return weak_phonemes
        else:
            return {}
            
    except Exception as e:
        print(f"Error fetching weak phonemes: {e}")
        return {}


def get_latest_session(client, user_id):
    """
    Get user's most recent session from Supabase.
    
    Args:
        client: Supabase client
        user_id: User identifier
    
    Returns:
        dict: Latest session data or None
    """
    try:
        response = client.from_('sessions')\
            .select('session_id, timestamp, sentence, transcription, overall_score, fluency_score')\
            .eq('user_id', user_id)\
            .order('timestamp', desc=True)\
            .limit(1)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching latest session: {e}")
        return None


def delete_user_data(client, user_id):
    """
    Delete all data for a specific user (GDPR compliance).
    
    Args:
        client: Supabase client
        user_id: User identifier
    
    Returns:
        bool: Success status
    """
    try:
        # Supabase will cascade delete due to foreign key constraints
        # Just delete the user profile
        client.from_('user_profiles').delete().eq('user_id', user_id).execute()
        return True
        
    except Exception as e:
        print(f"Error deleting user data: {e}")
        return False


def get_user_statistics(client, user_id):
    """
    Get comprehensive user statistics from Supabase.
    
    Args:
        client: Supabase client
        user_id: User identifier
    
    Returns:
        dict: User statistics
    """
    try:
        # Get all sessions for user
        sessions_response = client.from_('sessions')\
            .select('overall_score, fluency_score')\
            .eq('user_id', user_id)\
            .execute()
        
        if not sessions_response.data:
            return {
                'total_sessions': 0,
                'average_overall_score': 0,
                'average_fluency_score': 0,
                'best_score': 0,
                'total_practice_time': '0 minutes'
            }
        
        sessions = sessions_response.data
        total_sessions = len(sessions)
        
        overall_scores = [s['overall_score'] for s in sessions if s['overall_score'] is not None]
        fluency_scores = [s['fluency_score'] for s in sessions if s['fluency_score'] is not None]
        
        avg_overall = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
        best_score = max(overall_scores) if overall_scores else 0
        
        # Estimate practice time (30 seconds per session)
        total_practice_minutes = total_sessions * 0.5
        
        return {
            'total_sessions': total_sessions,
            'average_overall_score': round(avg_overall, 1),
            'average_fluency_score': round(avg_fluency, 1),
            'best_score': round(best_score, 1),
            'total_practice_time': f"{total_practice_minutes:.1f} minutes"
        }
        
    except Exception as e:
        print(f"Error fetching user statistics: {e}")
        return {
            'total_sessions': 0,
            'average_overall_score': 0,
            'average_fluency_score': 0,
            'best_score': 0,
            'total_practice_time': '0 minutes'
        }


# Admin functions
def get_all_users(client):
    """
    Get all users (admin only).
    
    Args:
        client: Supabase client
    
    Returns:
        list: List of all users
    """
    try:
        response = client.from_('user_profiles')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        
        return response.data if response.data else []
        
    except Exception as e:
        print(f"Error fetching all users: {e}")
        return []


def get_platform_statistics(client):
    """
    Get platform-wide statistics (admin only).
    
    Args:
        client: Supabase client
    
    Returns:
        dict: Platform statistics
    """
    try:
        # Total users
        users_response = client.from_('user_profiles').select('id', count='exact').execute()
        total_users = users_response.count if users_response.count else 0
        
        # Total sessions
        sessions_response = client.from_('sessions').select('session_id', count='exact').execute()
        total_sessions = sessions_response.count if sessions_response.count else 0
        
        # Active users (last 7 days)
        from datetime import timedelta
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        active_response = client.from_('user_profiles')\
            .select('id', count='exact')\
            .gte('last_active', week_ago)\
            .execute()
        active_users = active_response.count if active_response.count else 0
        
        return {
            'total_users': total_users,
            'total_sessions': total_sessions,
            'active_users_7d': active_users
        }
        
    except Exception as e:
        print(f"Error fetching platform statistics: {e}")
        return {
            'total_users': 0,
            'total_sessions': 0,
            'active_users_7d': 0
        }
