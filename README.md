---
title: AI Speech Therapy Platform
emoji: 🗣️
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.30.0
app_file: streamlit_app.py
pinned: false
---

# 🗣️ AI Speech Therapy Platform

An intelligent AI-powered pronunciation analysis and speech therapy application built with Streamlit.

## ✨ Features

- **🎙️ Audio Recording & Analysis**: Record your speech directly in the browser
- **🤖 AI-Powered Transcription**: Uses OpenAI Whisper for accurate speech-to-text
- **🔊 Phoneme-Level Scoring**: Analyzes pronunciation at the individual sound level using MFCC features
- **📊 Progress Tracking**: Comprehensive dashboards showing improvement over time
- **🎯 Smart Recommendations**: Personalized practice exercises based on your weak areas
- **💬 Detailed Feedback**: Clear, actionable feedback on pronunciation errors
- **🔐 Secure Authentication**: Role-based login/signup system (Admin & User)
- **👨‍💼 Admin Dashboard**: Platform management and user analytics
- **🗄️ Supabase Integration**: Cloud database for secure data storage

## 🚀 Quick Start

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd speech-therapy-platform
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser:**
   Navigate to `http://localhost:8501`

### Hugging Face Spaces Deployment

This app is designed to be deployed on Hugging Face Spaces:

1. Create a new Space on Hugging Face
2. Set SDK to "Streamlit"
3. Upload all files from this repository
4. The app will automatically deploy!

## 📖 How to Use

### 1. Practice Pronunciation
- Select or get a random practice sentence
- Click the microphone icon to record your pronunciation
- Click "Analyze My Pronunciation" to get instant feedback
- Review your scores and recommendations

### 2. Track Your Progress
- Navigate to the Dashboard page
- View your score trends over time
- See which phonemes you struggle with
- Review your recent practice sessions

### 3. Manage Settings
- View your unique user ID
- Reset your data if needed
- Learn about the app features

## 🏗️ Architecture

### Core Modules

- **`modules/audio_processor.py`**: Audio preprocessing, transcription (Whisper), phoneme conversion (G2P)
- **`modules/pronunciation_scorer.py`**: MFCC feature extraction and pronunciation scoring
- **`modules/feedback_generator.py`**: Converts scores to user-friendly feedback
- **`modules/recommender.py`**: Suggests targeted practice exercises
- **`modules/visualizer.py`**: Creates progress charts and visualizations

### Data Layer

- **`utils/db_utils.py`**: Supabase database operations for user progress and authentication
- **`utils/supabase_client.py`**: Supabase client initialization and connection management
- **`utils/audio_utils.py`**: Audio file manipulation helpers
- **`utils/text_utils.py`**: Text processing and comparison utilities
- **`auth_pages.py`**: Authentication pages (login/signup) and session management

### Data Files

- **`data/sentence_banks/`**: Practice sentences categorized by phoneme
- **`data/phoneme_mapping.json`**: Phoneme descriptions and articulation tips

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **Authentication**: Custom username/password with session management
- **Database**: Supabase (PostgreSQL)
- **Speech-to-Text**: OpenAI Whisper (via Transformers)
- **Phoneme Conversion**: g2p-en
- **Audio Processing**: librosa, torchaudio
- **Feature Extraction**: MFCC (Mel-Frequency Cepstral Coefficients)
- **Scoring**: Cosine similarity between user and reference embeddings
- **Visualization**: Plotly

## 📊 Scoring Methodology

The platform uses a multi-step scoring process:

1. **Preprocessing**: Audio is normalized, trimmed, and filtered
2. **Transcription**: Whisper converts speech to text
3. **Phoneme Extraction**: G2P converts text to phoneme sequences
4. **Alignment**: Phonemes are aligned to audio segments using time division
5. **Feature Extraction**: MFCC features are extracted from each segment
6. **Scoring**: Cosine similarity compares user features to reference embeddings
7. **Feedback Generation**: Scores are converted to actionable feedback

### Score Ranges

- **90-100**: Excellent pronunciation! 🏆
- **80-89**: Very good! 🌟
- **70-79**: Good work! 👍
- **60-69**: Fair, keep practicing! 📚
- **50-59**: Needs improvement 💪
- **Below 50**: Focus on basics 🎯

## 📁 Project Structure

```
speech-therapy-platform/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
│
├── modules/                    # Core processing modules
│   ├── audio_processor.py
│   ├── pronunciation_scorer.py
│   ├── feedback_generator.py
│   ├── recommender.py
│   └── visualizer.py
│
├── utils/                      # Utility functions
│   ├── db_utils.py
│   ├── audio_utils.py
│   └── text_utils.py
│
├── data/                       # Data files
│   ├── sentence_banks/
│   │   ├── general_practice.txt
│   │   ├── phoneme_th.txt
│   │   ├── phoneme_r.txt
│   │   ├── phoneme_l.txt
│   │   └── phoneme_v.txt
│   └── phoneme_mapping.json
│
├── database/                   # SQLite database storage
├── models/                     # Cached ML models
├── uploads/                    # User audio recordings
└── assets/                     # Static assets
```

## 🎯 Best Practices for Use

1. **Environment**: Record in a quiet space with minimal background noise
2. **Microphone**: Use a good quality microphone for best results
3. **Speaking**: Speak clearly and at a natural pace
4. **Consistency**: Practice regularly (daily recommended)
5. **Focus**: Work on recommended exercises for weak phonemes

## 🐛 Troubleshooting

### Audio Recording Issues
- Ensure microphone permissions are granted in your browser
- Check that your microphone is properly connected
- Try refreshing the page

### Slow Analysis
- First run may be slower due to model loading
- Subsequent analyses will be faster
- Consider using shorter sentences

### Low Scores
- Ensure you're reading the exact sentence shown
- Check your microphone quality
- Practice pronunciation before recording

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Contact

For questions or feedback, please open an issue on the repository.

## 🙏 Acknowledgments

- OpenAI for the Whisper model
- Hugging Face for the Transformers library
- Streamlit for the amazing web framework
- All contributors and users!

---

**Built with ❤️ using AI and open-source technologies**
