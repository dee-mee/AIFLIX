# AIFLIX - AI-Powered Streaming Platform

<img src="https://raw.githubusercontent.com/dee-mee/AIFLIX/master/images/banner.png" alt="AIFLIX Banner" width="700" height="400">

AIFLIX is a next-generation streaming platform that combines traditional entertainment with cutting-edge AI technology. Our platform offers both traditional content and AI-generated movies and series, providing a unique viewing experience tailored to each user's preferences.

## 🌟 About AIFLIX

### What is AIFLIX?
AIFLIX is a feature-rich streaming service that leverages artificial intelligence to transform how users discover and enjoy content. Our platform provides a seamless, Netflix-like experience with added intelligence to enhance your viewing journey.

### Key Features

#### 🎬 AI Content Library
- **AI-Generated Movies**: Watch movies created entirely by AI
- **AI-Upscaled Classics**: Enjoy classic movies in modern resolution
- **AI-Generated Series**: Follow original stories created by AI
- **Trending AI Content**: Discover what's popular in AI-generated content

#### 🎯 Smart Features
- **Profile-Based Recommendations**: Personalized suggestions for each profile
- **Watch History**: Track viewing progress across devices
- **Continue Watching**: Resume content from where you left off
- **My List**: Save content to watch later

#### 🎥 Streaming Experience
- **HD Video Quality**: High-definition streaming
- **Progress Tracking**: Save your viewing position
- **Rating System**: Rate content and influence recommendations

#### 👥 User Management
- **Multiple Profiles**: Create unique profiles for different viewers
- **Profile Selection**: Choose a profile before watching
- **Watch History**: Track viewing history per profile

## 🛠️ Technical Architecture

### Core Technologies
- **Backend**: Django 5.0.7 (Python)
- **Frontend**: Bootstrap 5, JavaScript, HTML5 Video
- **Database**: SQLite (Development)
- **Media Storage**: Local storage (Development)

### AI Components
- **AI Content Generation**: AI-generated movies and series
- **AI Upscaling**: Resolution enhancement for classic content
- **Content Analysis**: Automatic categorization and tagging
- **User Behavior**: Profile-based recommendations

## 🚀 Getting Started

### Local Development

[Previous content remains unchanged...]

## 🚀 Deployment to Render

### 1. Create a Render Account
- Sign up at https://render.com/
- Connect your GitHub account

### 2. Prepare Your Repository
- Ensure your repository contains:
  - `requirements.txt` with production dependencies
  - `Procfile` for web process
  - `runtime.txt` specifying Python version
  - `.env` file with production settings
  - `post-deploy` script for deployment tasks

### 3. Environment Variables
Set these environment variables in Render:

```bash
# Required
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*

# Database
DATABASE_URL=postgres://user:password@host:port/dbname

# Optional
CREATE_SUPERUSER=true
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_USERNAME=admin
```

### 4. Deploy to Render
1. Go to https://dashboard.render.com/
2. Click "New +" -> "Web Service"
3. Choose your repository
4. Select the main branch
5. Set environment variables
6. Click "Create Web Service"

### 5. Post-Deployment
After deployment, Render will automatically:
- Collect static files
- Apply database migrations
- Create superuser (if configured)
- Warm up cache

### Prerequisites
- Python 3.8+

### Development Workflow

1. **Branching Strategy**
   - `main`: Production-ready code
   - `develop`: Development branch
   - `feature/*`: Feature branches
   - `bugfix/*`: Bug fix branches

2. **Running Tests**
   ```bash
   python manage.py test
   ```

3. **Running Management Commands**
   ```bash
   # Create sample content
   python manage.py create_sample_content

   # Create AI content
   python manage.py create_ai_content
   ```

### Project Structure
```
AIFLIX/
├── aiflix/                 # Project settings
├── movies/                # Movie and TV show functionality
├── profiles/              # User profiles and watch history
├── accounts/              # Authentication system
├── static/               # Static files (CSS, JS, images)
└── templates/            # HTML templates
```

### Prerequisites
- Python 3.8+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dee-mee/AIFLIX.git
   cd AIFLIX
   ```

2. Create and activate virtual environment:
   ```bash
   # Linux/macOS
   python -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. Initialize database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

   The application will be available at http://127.0.0.1:8000/
