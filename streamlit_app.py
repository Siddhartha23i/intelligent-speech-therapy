"""
AI Speech Therapy Platform - Main Streamlit Application

A comprehensive pronunciation analysis and practice tool powered by AI.
"""

import streamlit as st
from datetime import datetime
import os

# Import custom modules
from modules.audio_processor import process_audio_full_pipeline
from modules.pronunciation_scorer import (
    load_or_create_reference_embeddings,
    score_pronunciation
)
from modules.feedback_generator import (
    generate_feedback,
    format_feedback_for_display,
    get_improvement_suggestions
)
from modules.recommender import (
    load_sentence_banks,
    get_recommendations,
    get_practice_plan
)
from modules.visualizer import (
    plot_score_trend,
    plot_phoneme_heatmap,
    display_session_summary,
    create_progress_summary_card
)
from utils.db_utils import (
    init_database,
    save_session,
    get_user_history,
    get_phoneme_statistics,
    get_user_statistics,
    get_latest_session,
    get_all_users,
    get_platform_statistics
)
from utils.text_utils import compare_sentences, highlight_differences
from auth_pages import (
    require_authentication,
    require_admin,
    logout,
    check_authentication
)
import random


# Page configuration
st.set_page_config(
    page_title="AI Speech Therapy Platform",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# NLTK Data Download
@st.cache_resource
def download_nltk_data():
    """Download required NLTK data."""
    import nltk
    packages = [
        'averaged_perceptron_tagger_eng',
        'averaged_perceptron_tagger',
        'cmudict',
        'punkt',
        'brown'
    ]
    for package in packages:
        try:
            nltk.download(package, quiet=True)
        except Exception as e:
            st.error(f"Failed to download NLTK package {package}: {e}")

try:
    download_nltk_data()
except Exception as e:
    st.error(f"Error setting up NLTK: {e}")


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    # User authentication is handled by auth_pages module
    # user_id, username, user_role are set after login
    
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = init_database()
    
    if 'current_sentence' not in st.session_state:
        sentence_banks = load_sentence_banks()
        general_sentences = sentence_banks.get('GENERAL', ["The quick brown fox jumps over the lazy dog."])
        st.session_state.current_sentence = random.choice(general_sentences)
    
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None


# Custom CSS
def load_custom_css():
    """Load custom CSS styling."""
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .sentence-display {
            font-size: 1.8rem;
            font-weight: 600;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .score-card {
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .excellent { background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); color: white; }
        .good { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; }
        .fair { background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); color: white; }
        .needs-practice { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; }
        
        /* Authentication Styles */
        .auth-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 2rem;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
    </style>
    """, unsafe_allow_html=True)


# Main Pages
def practice_page():
    """Main practice page with audio recording and analysis."""
    st.markdown('<div class="main-header">🎙️ Practice Pronunciation</div>', unsafe_allow_html=True)
    
    # Sentence selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sentence_banks = load_sentence_banks()
        all_sentences = []
        for sentences in sentence_banks.values():
            all_sentences.extend(sentences)
        
        selected_sentence = st.selectbox(
            "Choose a practice sentence or select random:",
            options=all_sentences,
            index=all_sentences.index(st.session_state.current_sentence) if st.session_state.current_sentence in all_sentences else 0,
            key='sentence_selector'
        )
        st.session_state.current_sentence = selected_sentence
    
    with col2:
        if st.button("🎲 Random Sentence", use_container_width=True):
            st.session_state.current_sentence = random.choice(all_sentences)
            st.rerun()
    
    # Display selected sentence
    st.markdown(f'<div class="sentence-display">{st.session_state.current_sentence}</div>', 
                unsafe_allow_html=True)
    
    # Audio recording
    st.markdown("### 📝 Record Your Pronunciation")
    st.info("💡 **Tip:** Speak clearly and at a natural pace. Make sure you're in a quiet environment.")
    
    audio_file = st.audio_input("Click to start recording:")
    
    # Analysis button
    if audio_file is not None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_button = st.button(
                "🔍 Analyze My Pronunciation",
                use_container_width=True,
                type="primary"
            )
        
        if analyze_button:
            with st.spinner("🎯 Analyzing your pronunciation... This may take a few moments."):
                # Process audio
                result = process_audio_full_pipeline(
                    audio_file,
                    expected_sentence=st.session_state.current_sentence
                )
                
                if result['success']:
                    # Load reference embeddings
                    ref_embeddings = load_or_create_reference_embeddings()
                    
                    # Score pronunciation
                    score_data = score_pronunciation(
                        result['alignments'],
                        ref_embeddings
                    )
                    
                    # Generate feedback
                    feedback = generate_feedback(
                        score_data,
                        result['transcription'],
                        st.session_state.current_sentence
                    )
                    
                    # Save to database
                    session_id = save_session(
                        st.session_state.db_conn,
                        st.session_state.user_id,
                        st.session_state.current_sentence,
                        result['transcription'],
                        score_data
                    )
                    
                    # Store result
                    st.session_state.last_result = {
                        'score_data': score_data,
                        'feedback': feedback,
                        'transcription': result['transcription'],
                        'session_id': session_id
                    }
                else:
                    st.error(f"❌ Error processing audio: {result.get('error', 'Unknown error')}")
                    return
            
            # Display results
            st.success("✅ Analysis complete!")
    
    # Show results if available
    if st.session_state.last_result:
        st.markdown("---")
        st.markdown("## 📊 Your Results")
        
        result = st.session_state.last_result
        score_data = result['score_data']
        feedback = result['feedback']
        
        # Display session summary
        display_session_summary(score_data)
        
        # Feedback section
        st.markdown("### 💬 Personalized Feedback")
        formatted_feedback = format_feedback_for_display(feedback)
        
        # Main encouragement
        st.info(f"{formatted_feedback['score_emoji']} {formatted_feedback['main_message']}")
        
        # Detailed feedback
        if formatted_feedback['detailed_feedback']:
            st.markdown(formatted_feedback['detailed_feedback'])
        
        # Transcription comparison
        with st.expander("📝 Transcription Details", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Expected:**")
                st.write(st.session_state.current_sentence)
            with col2:
                st.markdown("**You said:**")
                st.write(result['transcription'])
            
            # Show highlighted differences
            st.markdown("**Comparison:**")
            highlighted = highlight_differences(
                st.session_state.current_sentence,
                result['transcription']
            )
            st.markdown(highlighted)
        
        # Practice recommendations
        st.markdown("### 🎯 Recommended Practice")
        weak_phonemes = score_data.get('weak_phonemes', [])
        recommendations = get_recommendations(weak_phonemes, num_sentences=3)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority_color = "🔴" if rec['priority'] == 'high' else "🟡"
                st.markdown(f"{priority_color} **{i}.** {rec['sentence']}")
                st.caption(f"Focus: {rec['focus']}")
        else:
            st.success("🎉 Excellent work! Keep practicing with varied sentences.")


def dashboard_page():
    """Progress dashboard page."""
    st.markdown('<div class="main-header">📈 Your Progress Dashboard</div>', unsafe_allow_html=True)
    
    # Get user statistics
    user_stats = get_user_statistics(st.session_state.db_conn, st.session_state.user_id)
    
    if user_stats['total_sessions'] == 0:
        st.info("👋 Welcome! Complete your first practice session to see your progress here.")
        return
    
    # Display overall statistics
    st.markdown("### 📊 Overall Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sessions", user_stats['total_sessions'])
    with col2:
        st.metric("Average Score", f"{user_stats['average_overall_score']:.1f}")
    with col3:
        st.metric("Best Score", f"{user_stats['best_score']:.1f}")
    with col4:
        st.metric("Practice Time", user_stats['total_practice_time'])
    
    st.markdown("---")
    
    # Score trend chart
    st.markdown("### 📈 Score Trend")
    history_df = get_user_history(st.session_state.db_conn, st.session_state.user_id)
    
    if not history_df.empty:
        fig_trend = plot_score_trend(history_df)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Phoneme performance
    st.markdown("### 🎵 Phoneme Performance")
    phoneme_stats = get_phoneme_statistics(st.session_state.db_conn, st.session_state.user_id)
    
    if phoneme_stats:
        fig_phonemes = plot_phoneme_heatmap(phoneme_stats)
        st.plotly_chart(fig_phonemes, use_container_width=True)
        
        # Show table of weakest phonemes
        with st.expander("📋 Detailed Phoneme Statistics"):
            import pandas as pd
            df = pd.DataFrame.from_dict(phoneme_stats, orient='index')
            df = df.sort_values('average_score')
            st.dataframe(df, use_container_width=True)
    
    # Recent sessions
    st.markdown("### 📜 Recent Sessions")
    if not history_df.empty:
        display_df = history_df[['timestamp', 'sentence', 'overall_score', 'fluency_score']].head(10)
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['Date', 'Sentence', 'Score', 'Fluency']
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def settings_page():
    """Settings and configuration page."""
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    # User Profile
    st.markdown("### 👤 User Profile")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Username:** `{st.session_state.get('username', 'N/A')}`")
        st.info(f"**Full Name:** {st.session_state.get('full_name', 'N/A')}")
    
    with col2:
        role = st.session_state.get('user_role', 'user')
        role_display = "👨‍💼 Administrator" if role == 'admin' else "👤 Regular User"
        st.info(f"**Role:** {role_display}")
        st.info(f"**User ID:** `{st.session_state.get('user_id', 'N/A')[:8]}...`")
    
    st.markdown("---")
    
    # Statistics
    st.markdown("### 📊 Account Statistics")
    stats = get_user_statistics(st.session_state.db_conn, st.session_state.user_id)
    st.write(f"- Total practice sessions: **{stats['total_sessions']}**")
    st.write(f"- Total practice time: **{stats['total_practice_time']}**")
    st.write(f"- Best score: **{stats['best_score']}**")
    
    st.markdown("---")
    
    # Logout
    st.markdown("### � Account Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("� Logout", use_container_width=True, type="primary"):
            logout()
    
    with col2:
        if st.button("🗑️ Delete My Data", help="Permanently delete all your practice data", use_container_width=True):
            from utils.db_utils import delete_user_data
            if delete_user_data(st.session_state.db_conn, st.session_state.user_id):
                st.success("✅ All data deleted successfully!")
                logout()
            else:
                st.error("❌ Error deleting data.")
    
    st.markdown("---")
    
    # About
    st.markdown("### ℹ️ About")
    st.markdown("""
    **AI Speech Therapy Platform v2.0 with Authentication**
    
    This application uses advanced AI technology to help you improve your pronunciation:
    - 🎙️ **Speech Recognition:** OpenAI Whisper for accurate transcription
    - 🔊 **Phoneme Analysis:** MFCC-based pronunciation scoring
    - 📊 **Progress Tracking:** Comprehensive performance analytics
    - 🎯 **Smart Recommendations:** Personalized practice suggestions
    - 🔐 **Secure Authentication:** Role-based access with Supabase
    
    **Tips for Best Results:**
    - Use a quiet environment
    - Speak clearly and naturally
    - Practice regularly for improvement
    - Focus on recommended exercises
    """)


def admin_dashboard_page():
    """Admin dashboard for managing platform and users."""
    st.markdown('<div class="main-header">👨‍💼 Admin Dashboard</div>', unsafe_allow_html=True)
    
    if not require_admin():
        st.error("❌ Access Denied: Admin privileges required")
        return
    
    # Platform Statistics
    st.markdown("### 📊 Platform Statistics")
    platform_stats = get_platform_statistics(st.session_state.db_conn)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", platform_stats['total_users'])
    with col2:
        st.metric("Total Sessions", platform_stats['total_sessions'])
    with col3:
        st.metric("Active Users (7 days)", platform_stats['active_users_7d'])
    
    st.markdown("---")
    
    # User Management
    st.markdown("### 👥 User Management")
    
    all_users = get_all_users(st.session_state.db_conn)
    
    if all_users:
        import pandas as pd
        
        # Convert to DataFrame for display
        users_df = pd.DataFrame(all_users)
        
        # Select relevant columns
        display_columns = ['username', 'full_name', 'role', 'created_at', 'last_active']
        available_columns = [col for col in display_columns if col in users_df.columns]
        
        if available_columns:
            display_df = users_df[available_columns].copy()
            
            # Format timestamps
            for col in ['created_at', 'last_active']:
                if col in display_df.columns:
                    display_df[col] = pd.to_datetime(display_df[col]).dt.strftime('%Y-%m-%d %H:%M')
            
            # Rename columns for display
            column_rename = {
                'username': 'Username',
                'full_name': 'Full Name',
                'role': 'Role',
                'created_at': 'Created',
                'last_active': 'Last Active'
            }
            display_df = display_df.rename(columns=column_rename)
            
            # Display table
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.caption(f"Total users: {len(all_users)}")
    else:
        st.info("No users found in the system.")
    
    st.markdown("---")
    
    # Recent Activity
    st.markdown("### 📈 Recent Platform Activity")
    
    # This could be enhanced to show recent sessions from all users
    st.info("Feature coming soon: Real-time activity feed")


# Main app
def main():
    """Main application entry point."""
    # Initialize
    init_session_state()
    load_custom_css()
    
    # Require authentication - show login/signup if not authenticated
    if not require_authentication():
        return
    
    # Sidebar navigation
    st.sidebar.title("🗣️ AI Speech Therapy")
    st.sidebar.markdown(f"**Welcome, {st.session_state.get('username', 'User')}!**")
    
    # Show role badge
    role = st.session_state.get('user_role', 'user')
    if role == 'admin':
        st.sidebar.markdown("🔑 **Administrator**")
    
    st.sidebar.markdown("---")
    
    # Navigation options
    nav_options = ["🎙️ Practice", "📈 Dashboard", "⚙️ Settings"]
    
    # Add admin dashboard for admins
    if role == 'admin':
        nav_options.insert(2, "👨‍💼 Admin")
    
    page = st.sidebar.radio(
        "Navigate",
        nav_options,
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Quick Tips")
    st.sidebar.info("""
    - Record in a quiet place
    - Speak clearly and naturally
    - Practice daily for best results
    - Review your weak sounds
    """)
    
    # Route to appropriate page
    if page == "🎙️ Practice":
        practice_page()
    elif page == "📈 Dashboard":
        dashboard_page()
    elif page == "👨‍💼 Admin":
        admin_dashboard_page()
    elif page == "⚙️ Settings":
        settings_page()


if __name__ == "__main__":
    main()
