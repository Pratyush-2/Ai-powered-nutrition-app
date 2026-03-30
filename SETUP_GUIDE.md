# 🚀 Complete Setup Guide

## Prerequisites

- **Python 3.11+** installed
- **Flutter SDK** installed (for mobile app)
- **Git** installed
- **Code editor** (VS Code recommended)

## 📋 Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Pratyush-2/ai-powered-nutrition-app.git
cd ai-powered-nutrition-app
```

### 2. Backend Setup (FastAPI)

#### Create Virtual Environment
```bash
python -m venv venv
```

#### Activate Virtual Environment
```bash
# Windows PowerShell:
venv\Scripts\activate

# Windows Command Prompt:
venv\Scripts\activate.bat

# macOS/Linux:
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Set Up Environment Variables
```bash
# Copy example file
cp .env.example .env    # Linux/macOS
copy .env.example .env  # Windows

# Edit .env with your actual credentials
```

**Required in `.env`:**
- `DATABASE_URL` — Database connection string (default: `sqlite:///./data/app.db`)
- `OPENAI_API_KEY` — Your OpenAI API key (for LLM features)
- `GOOGLE_APPLICATION_CREDENTIALS` — Path to your Google Cloud Vision credentials JSON

> **Note:** See `.env.example` for the full list of available configuration options.

#### Initialize Database
```bash
python app/create_tables.py
```

#### Start FastAPI Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify Backend:**
- Open http://localhost:8000/docs for interactive API documentation
- Test endpoint: http://localhost:8000/search-food/apple

### 3. Frontend Setup (Flutter)

#### Navigate to Flutter App
```bash
cd nutrition_app
```

#### Install Dependencies
```bash
flutter pub get
```

#### Run Flutter App
```bash
# For Android
flutter run

# For iOS (Mac only)
flutter run -d ios

# For Web
flutter run -d chrome
```

### 4. Google Cloud Vision Setup (Optional)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Vision API** for your project
3. Create a **Service Account** with Vision API access
4. Download the credentials JSON file
5. Place it in the project root (it is automatically gitignored via `*.json` pattern)
6. Set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=your-credentials-file.json
   ```

> ⚠️ **Important:** Never commit credential files to git. All `*.json` files in the project root are gitignored by default.

### 5. Verify Installation

#### Test Backend API
```bash
# Test food search
curl http://localhost:8000/search-food/apple

# Test AI health endpoint
curl http://localhost:8000/ai/health/
```

#### Test Flutter App
1. Open the app on your device/emulator
2. Search for "apple"
3. Add food to log
4. Check that recommendations appear

## 🔧 Troubleshooting

### Backend Issues

**Port Already in Use:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000   # Windows
lsof -i :8000                  # macOS/Linux

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

**Import Errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Database Errors:**
- Delete existing database files in `data/`
- Run `python app/create_tables.py` again

### Flutter Issues

**Build Errors:**
```bash
flutter clean
flutter pub get
flutter run
```

**API Connection Errors:**
- Verify backend is running on port 8000
- Check `baseUrl` in `nutrition_app/lib/services/api_service.dart`
- Ensure firewall allows localhost connections

## 📁 Project Structure

```
ai-powered-nutrition-app/
├── app/                    # FastAPI backend
│   ├── ai/                # AI routes and services
│   ├── ai_pipeline/       # AI processing pipeline
│   ├── services/          # Food search and services
│   ├── models.py          # Database models
│   ├── schemas.py         # Pydantic schemas
│   └── main.py            # FastAPI app entry point
├── nutrition_app/          # Flutter mobile app
│   ├── lib/               # Dart source code
│   └── pubspec.yaml       # Flutter dependencies
├── tests/                  # Test suite
├── scripts/                # Utility scripts
├── data/                   # Data storage (gitignored)
├── .env.example            # Environment variable template
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker build config
├── docker-compose.yml      # Docker Compose config
└── README.md               # Project documentation
```

## ✅ Quick Start Checklist

- [ ] Python 3.11+ installed
- [ ] Flutter SDK installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from `.env.example`
- [ ] Database initialized (`python app/create_tables.py`)
- [ ] Backend running (`uvicorn app.main:app --reload`)
- [ ] Flutter dependencies installed (`flutter pub get`)
- [ ] Flutter app running (`flutter run`)

---

For more details, see the [README](README.md) or open an issue on GitHub.
