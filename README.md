# AIFLIX - Intelligent Movie & TV Show Streaming Platform

![AIFLIX Banner](https://via.placeholder.com/1200x400/141414/ffffff?text=AIFLIX+Streaming+Platform)

AIFLIX is an intelligent streaming platform that combines the best of entertainment with cutting-edge AI technology. Designed to deliver a personalized viewing experience, AIFLIX offers a vast library of movies and TV shows with smart recommendations tailored to each user's preferences.

## 🌟 About AIFLIX

### What is AIFLIX?
AIFLIX is a feature-rich streaming service that leverages artificial intelligence to transform how users discover and enjoy content. Our platform provides a seamless, Netflix-like experience with added intelligence to enhance your viewing journey.

### Key Features

#### 🎬 Smart Content Discovery
- **AI-Powered Recommendations**: Get personalized suggestions based on your viewing history and preferences
- **Trending Now**: Stay updated with what's popular in your region
- **Custom Categories**: Discover content through intelligently curated categories

#### 👥 User Experience
- **Multiple Profiles**: Create up to 5 unique profiles per account
- **Watch History**: Never lose track of where you left off
- **Continue Watching**: Seamlessly pick up where you left off across devices

#### 🎥 High-Quality Streaming
- **Adaptive Bitrate**: Smooth streaming at any internet speed
- **HD/4K Support**: Crystal clear video quality
- **Offline Viewing**: Download content to watch later

#### 🔒 Secure & Private
- **End-to-End Encryption**: Your data stays private
- **Parental Controls**: Safe viewing for all ages
- **Secure Payments**: Multiple payment options with bank-level security

## 🛠️ Technical Architecture

### Core Technologies
- **Backend**: Django 5.0.7 (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Search**: Full-text search with PostgreSQL
- **Caching**: Redis for improved performance
- **Media Storage**: AWS S3 for scalable media storage

### AI/ML Components
- **Recommendation Engine**: Collaborative filtering and content-based filtering
- **Content Analysis**: Automatic tagging and categorization
- **User Behavior Analysis**: Personalized content discovery

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/dee-mee/AIFLIX.git](https://github.com/dee-mee/AIFLIX.git)
   cd AIFLIX
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate


# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt


cp .env.example .env


# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_NAME=aiflix
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@aiflix.com

# AWS S3 (for media storage)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name



sudo -u postgres createdb aiflix
sudo -u postgres createuser -P aiflix_user
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aiflix TO aiflix_user;"


python manage.py migrate
