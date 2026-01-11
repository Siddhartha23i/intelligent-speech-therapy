<<<<<<< HEAD
"""
Visualization Module for Speech Therapy Platform

This module creates progress tracking visualizations:
- Score trend charts
- Phoneme performance heatmaps
- Session summaries
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime


def plot_score_trend(user_history_df):
    """
    Create a line chart showing score progression over time.
    
    Args:
        user_history_df: DataFrame with user's session history
    
    Returns:
        plotly.graph_objects.Figure: Score trend chart
    """
    if user_history_df.empty:
        # Create empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No practice history yet. Complete a few sessions to see your progress!",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            title="Score Progress Over Time",
            xaxis_title="Date",
            yaxis_title="Score",
            height=400
        )
        return fig
    
    # Create line chart
    fig = go.Figure()
    
    # Add overall score line
    fig.add_trace(go.Scatter(
        x=user_history_df['timestamp'],
        y=user_history_df['overall_score'],
        mode='lines+markers',
        name='Overall Score',
        line=dict(color='royalblue', width=3),
        marker=dict(size=8)
    ))
    
    # Add trend line
    if len(user_history_df) > 2:
        z = np.polyfit(range(len(user_history_df)), user_history_df['overall_score'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=user_history_df['timestamp'],
            y=p(range(len(user_history_df))),
            mode='lines',
            name='Trend',
            line=dict(color='lightcoral', width=2, dash='dash')
        ))
    
    # Update layout
    fig.update_layout(
        title="Your Pronunciation Progress",
        xaxis_title="Date",
        yaxis_title="Score (0-100)",
        yaxis=dict(range=[0, 100]),
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    return fig


def plot_phoneme_heatmap(phoneme_stats):
    """
    Create a bar chart showing average score per phoneme.
    
    Args:
        phoneme_stats: Dictionary with phoneme statistics
    
    Returns:
        plotly.graph_objects.Figure: Phoneme performance chart
    """
    if not phoneme_stats:
        # Create empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="Complete a practice session to see phoneme analysis!",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            title="Phoneme Performance",
            xaxis_title="Phoneme",
            yaxis_title="Average Score",
            height=400
        )
        return fig
    
    # Prepare data
    phonemes = list(phoneme_stats.keys())
    scores = [phoneme_stats[p]['average_score'] for p in phonemes]
    counts = [phoneme_stats[p]['count'] for p in phonemes]
    
    # Color code based on score
    colors = []
    for score in scores:
        if score >= 80:
            colors.append('#2ecc71')  # Green
        elif score >= 60:
            colors.append('#f39c12')  # Yellow
        else:
            colors.append('#e74c3c')  # Red
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=phonemes,
        y=scores,
        marker_color=colors,
        text=[f"{s:.1f}" for s in scores],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Average Score: %{y:.1f}<br>Practiced: %{customdata} times<extra></extra>',
        customdata=counts
    ))
    
    # Add reference lines
    fig.add_hline(y=80, line_dash="dash", line_color="green", 
                  annotation_text="Good (80)", annotation_position="right")
    fig.add_hline(y=60, line_dash="dash", line_color="orange",
                  annotation_text="Needs Practice (60)", annotation_position="right")
    
    # Update layout
    fig.update_layout(
        title="Phoneme Performance Overview",
        xaxis_title="Phoneme",
        yaxis_title="Average Score (0-100)",
        yaxis=dict(range=[0, 100]),
        height=500,
        template='plotly_white',
        showlegend=False
    )
    
    return fig


def display_session_summary(session_data):
    """
    Display a comprehensive session summary using Streamlit components.
    
    Args:
        session_data: Dictionary with session results
    """
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Overall Score",
            f"{session_data.get('overall_score', 0):.1f}",
            delta=None,
            help="Your overall pronunciation score for this session"
        )
    
    with col2:
        st.metric(
            "Fluency Score",
            f"{session_data.get('fluency_score', 0):.1f}",
            delta=None,
            help="Consistency of your pronunciation across all sounds"
        )
    
    with col3:
        total_phonemes = session_data.get('total_phonemes', 0)
        weak_count = len(session_data.get('weak_phonemes', []))
        accuracy = ((total_phonemes - weak_count) / total_phonemes * 100) if total_phonemes > 0 else 0
        st.metric(
            "Accuracy",
            f"{accuracy:.0f}%",
            delta=None,
            help="Percentage of sounds pronounced correctly"
        )


def create_phoneme_distribution(phoneme_scores):
    """
    Create a distribution chart of phoneme scores.
    
    Args:
        phoneme_scores: List of dictionaries with phoneme scores
    
    Returns:
        plotly.graph_objects.Figure: Distribution chart
    """
    if not phoneme_scores:
        return None
    
    scores = [p['score'] for p in phoneme_scores]
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=scores,
        nbinsx=20,
        marker_color='skyblue',
        opacity=0.75
    ))
    
    fig.update_layout(
        title="Score Distribution",
        xaxis_title="Score Range",
        yaxis_title="Number of Phonemes",
        height=300,
        template='plotly_white'
    )
    
    return fig


def create_progress_summary_card(latest_score, previous_score=None):
    """
    Create a visual progress summary card.
    
    Args:
        latest_score: Most recent session score
        previous_score: Previous session score (for comparison)
    
    Returns:
        dict: Summary data for display
    """
    improvement = None
    if previous_score is not None:
        improvement = latest_score - previous_score
    
    # Determine status
    if latest_score >= 90:
        status = "Excellent"
        color = "green"
        emoji = "🏆"
    elif latest_score >= 80:
        status = "Very Good"
        color = "lightgreen"
        emoji = "🌟"
    elif latest_score >= 70:
        status = "Good"
        color = "yellow"
        emoji = "👍"
    elif latest_score >= 60:
        status = "Fair"
        color = "orange"
        emoji = "📚"
    else:
        status = "Needs Practice"
        color = "red"
        emoji = "💪"
    
    return {
        'status': status,
        'color': color,
        'emoji': emoji,
        'score': latest_score,
        'improvement': improvement
    }
=======
"""
Visualization Module for Speech Therapy Platform

This module creates progress tracking visualizations:
- Score trend charts
- Phoneme performance heatmaps
- Session summaries
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime


def plot_score_trend(user_history_df):
    """
    Create a line chart showing score progression over time.
    
    Args:
        user_history_df: DataFrame with user's session history
    
    Returns:
        plotly.graph_objects.Figure: Score trend chart
    """
    if user_history_df.empty:
        # Create empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No practice history yet. Complete a few sessions to see your progress!",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            title="Score Progress Over Time",
            xaxis_title="Date",
            yaxis_title="Score",
            height=400
        )
        return fig
    
    # Create line chart
    fig = go.Figure()
    
    # Add overall score line
    fig.add_trace(go.Scatter(
        x=user_history_df['timestamp'],
        y=user_history_df['overall_score'],
        mode='lines+markers',
        name='Overall Score',
        line=dict(color='royalblue', width=3),
        marker=dict(size=8)
    ))
    
    # Add trend line
    if len(user_history_df) > 2:
        z = np.polyfit(range(len(user_history_df)), user_history_df['overall_score'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=user_history_df['timestamp'],
            y=p(range(len(user_history_df))),
            mode='lines',
            name='Trend',
            line=dict(color='lightcoral', width=2, dash='dash')
        ))
    
    # Update layout
    fig.update_layout(
        title="Your Pronunciation Progress",
        xaxis_title="Date",
        yaxis_title="Score (0-100)",
        yaxis=dict(range=[0, 100]),
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    return fig


def plot_phoneme_heatmap(phoneme_stats):
    """
    Create a bar chart showing average score per phoneme.
    
    Args:
        phoneme_stats: Dictionary with phoneme statistics
    
    Returns:
        plotly.graph_objects.Figure: Phoneme performance chart
    """
    if not phoneme_stats:
        # Create empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="Complete a practice session to see phoneme analysis!",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            title="Phoneme Performance",
            xaxis_title="Phoneme",
            yaxis_title="Average Score",
            height=400
        )
        return fig
    
    # Prepare data
    phonemes = list(phoneme_stats.keys())
    scores = [phoneme_stats[p]['average_score'] for p in phonemes]
    counts = [phoneme_stats[p]['count'] for p in phonemes]
    
    # Color code based on score
    colors = []
    for score in scores:
        if score >= 80:
            colors.append('#2ecc71')  # Green
        elif score >= 60:
            colors.append('#f39c12')  # Yellow
        else:
            colors.append('#e74c3c')  # Red
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=phonemes,
        y=scores,
        marker_color=colors,
        text=[f"{s:.1f}" for s in scores],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Average Score: %{y:.1f}<br>Practiced: %{customdata} times<extra></extra>',
        customdata=counts
    ))
    
    # Add reference lines
    fig.add_hline(y=80, line_dash="dash", line_color="green", 
                  annotation_text="Good (80)", annotation_position="right")
    fig.add_hline(y=60, line_dash="dash", line_color="orange",
                  annotation_text="Needs Practice (60)", annotation_position="right")
    
    # Update layout
    fig.update_layout(
        title="Phoneme Performance Overview",
        xaxis_title="Phoneme",
        yaxis_title="Average Score (0-100)",
        yaxis=dict(range=[0, 100]),
        height=500,
        template='plotly_white',
        showlegend=False
    )
    
    return fig


def display_session_summary(session_data):
    """
    Display a comprehensive session summary using Streamlit components.
    
    Args:
        session_data: Dictionary with session results
    """
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Overall Score",
            f"{session_data.get('overall_score', 0):.1f}",
            delta=None,
            help="Your overall pronunciation score for this session"
        )
    
    with col2:
        st.metric(
            "Fluency Score",
            f"{session_data.get('fluency_score', 0):.1f}",
            delta=None,
            help="Consistency of your pronunciation across all sounds"
        )
    
    with col3:
        total_phonemes = session_data.get('total_phonemes', 0)
        weak_count = len(session_data.get('weak_phonemes', []))
        accuracy = ((total_phonemes - weak_count) / total_phonemes * 100) if total_phonemes > 0 else 0
        st.metric(
            "Accuracy",
            f"{accuracy:.0f}%",
            delta=None,
            help="Percentage of sounds pronounced correctly"
        )


def create_phoneme_distribution(phoneme_scores):
    """
    Create a distribution chart of phoneme scores.
    
    Args:
        phoneme_scores: List of dictionaries with phoneme scores
    
    Returns:
        plotly.graph_objects.Figure: Distribution chart
    """
    if not phoneme_scores:
        return None
    
    scores = [p['score'] for p in phoneme_scores]
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=scores,
        nbinsx=20,
        marker_color='skyblue',
        opacity=0.75
    ))
    
    fig.update_layout(
        title="Score Distribution",
        xaxis_title="Score Range",
        yaxis_title="Number of Phonemes",
        height=300,
        template='plotly_white'
    )
    
    return fig


def create_progress_summary_card(latest_score, previous_score=None):
    """
    Create a visual progress summary card.
    
    Args:
        latest_score: Most recent session score
        previous_score: Previous session score (for comparison)
    
    Returns:
        dict: Summary data for display
    """
    improvement = None
    if previous_score is not None:
        improvement = latest_score - previous_score
    
    # Determine status
    if latest_score >= 90:
        status = "Excellent"
        color = "green"
        emoji = "🏆"
    elif latest_score >= 80:
        status = "Very Good"
        color = "lightgreen"
        emoji = "🌟"
    elif latest_score >= 70:
        status = "Good"
        color = "yellow"
        emoji = "👍"
    elif latest_score >= 60:
        status = "Fair"
        color = "orange"
        emoji = "📚"
    else:
        status = "Needs Practice"
        color = "red"
        emoji = "💪"
    
    return {
        'status': status,
        'color': color,
        'emoji': emoji,
        'score': latest_score,
        'improvement': improvement
    }
>>>>>>> 91fcca26e074a943dc9c8fb178dacc68158b4847
