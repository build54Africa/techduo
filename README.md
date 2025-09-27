# MergeSensei 🤖

**AI-Powered Git Conflict Prediction and Resolution Platform**

MergeSensei is an intelligent system that predicts merge conflicts before they happen and provides actionable recommendations to resolve them. Built with Django REST Framework and Vue.js, it combines machine learning models with AI services to help development teams avoid merge conflicts and streamline their Git workflows.

## 🌟 Features

- **AI-Powered Conflict Prediction**: Uses Cohere and OpenRouter AI models to predict merge conflicts
- **GitHub Integration**: Seamlessly connects with GitHub repositories to analyze pull requests
- **Risk Assessment**: Provides detailed risk scores and confidence levels for each PR
- **Smart Recommendations**: Generates actionable suggestions for conflict resolution
- **Real-time Analysis**: Live analysis of pull requests with instant feedback
- **Machine Learning Models**: Trains on historical data to improve prediction accuracy
- **Modern UI**: Beautiful, responsive interface built with Vue.js and Tailwind CSS

## 🏗️ Tech Stack

### Backend
- **Django 5.2.6** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database
- **Python 3.13** - Programming language

### Frontend
- **Vue.js 3.5.18** - Progressive JavaScript framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Data visualization
- **Pinia** - State management

### AI & ML
- **Cohere API** - Natural language processing
- **OpenRouter** - AI model access
- **scikit-learn** - Machine learning library
- **pandas** - Data manipulation

### DevOps & Deployment
- **Render** - Cloud hosting platform
- **PostgreSQL** - Production database

## 🚀 Live Demo

**Hosted on Render**: [https://mergesensei.onrender.com](https://mergesensei.onrender.com)

## 📋 Prerequisites

- Python 3.13+
- Node.js 20.19.0+ or 22.12.0+
- PostgreSQL 12+
- Git

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/techduo.git
cd techduo
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration:
# DB_NAME=mergesensei
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=5432
# OPENROUTER_API_KEY=your_openrouter_key
# COHERE_API_KEY=your_cohere_key

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 4. Database Setup

Make sure PostgreSQL is running and create a database:

```sql
CREATE DATABASE mergesensei;
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DB_NAME=mergesensei
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# AI Service Keys
OPENROUTER_API_KEY=your_openrouter_api_key
COHERE_API_KEY=your_cohere_api_key

# Django Settings
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### API Keys Setup

1. **OpenRouter**: Sign up at [OpenRouter](https://openrouter.ai/) and get your API key
2. **Cohere**: Sign up at [Cohere](https://cohere.ai/) and get your API key

## 🚀 Running the Application

### Development Mode

1. **Start Backend**:
   ```bash
   cd backend
   python manage.py runserver
   ```
   Backend will be available at: `http://localhost:8000`

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will be available at: `http://localhost:5173`

### Production Mode

```bash
# Build frontend
cd frontend
npm run build

# Start backend in production
cd backend
python manage.py collectstatic
python manage.py runserver 0.0.0.0:8000
```

## 📚 API Documentation

### Core Endpoints

- `GET /api/health/` - Health check
- `POST /api/risk/` - Analyze conflict risk
- `POST /api/recommendation/` - Get AI recommendations
- `POST /api/predict/` - Predict conflicts using ML
- `GET /api/ai-status/` - Check AI service status

### GitHub Integration

- `GET /api/github/status/` - GitHub connection status
- `POST /api/github/connect/` - Connect repository
- `POST /api/github/analyze/` - Analyze GitHub PR
- `GET /api/github/search/` - Search repositories

### Example API Usage

```bash
# Analyze a pull request
curl -X POST http://localhost:8000/api/risk/ \
  -H "Content-Type: application/json" \
  -d '{
    "pr_number": 123,
    "repo_name": "my-repo",
    "repo_owner": "my-username"
  }'
```

## 🧪 Testing

```bash
# Run backend tests
cd backend
python manage.py test

# Run frontend tests
cd frontend
npm test
```

## 📁 Project Structure