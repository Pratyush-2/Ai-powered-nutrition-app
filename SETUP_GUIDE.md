# 🚀 Complete Setup Guide

## Prerequisites

- **Python 3.8+** installed
- **Flutter SDK** installed (for mobile app)
- **Git** installed
- **Code editor** (VS Code recommended)

## 📋 Step-by-Step Setup

### 1. Clone/Download Repository

```bash
cd "C:\Users\Praty\OneDrive\Desktop\Proj fast_api - Copy (3)"
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
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Set Up Environment Variables
```bash
# Copy example file
copy .env.example .env

# Edit .env with your actual credentials
notepad .env
```

**Required in .env:**
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to your Google Cloud Vision credentials JSON file
- `DATABASE_URL` - Database connection string (default: `sqlite:///./data/app.db`)
- `OLLAMA_URL` - Ollama API URL (default: `http://localhost:11434/api/generate`)

#### Initialize Database
```bash
python app/create_tables.py
```

#### Start FastAPI Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify Backend:**
- Open http://localhost:8000/docs for API documentation
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

### 4. Google Cloud Vision Setup

1. **Create Project** in Google Cloud Console
2. **Enable Vision API** for your project
3. **Create Service Account** with Vision API access
4. **Download Credentials** as JSON file
5. **Place credentials** in project root as `analog-reef-470415-q6-b8ddae1e11b3.json`
6. **Set environment variable** (optional):
   ```bash
   set GOOGLE_APPLICATION_CREDENTIALS=analog-reef-470415-q6-b8ddae1e11b3.json
   ```

**⚠️ Important:** The credentials file is in `.gitignore` and should NEVER be committed to git!

### 5. Verify Installation

#### Test Backend API
```bash
# Test food search
python -c "import requests; r = requests.get('http://localhost:8000/search-food/apple'); print('Status:', r.status_code, 'Products:', len(r.json().get('products', [])))"

# Test food classification
python -c "import requests; r = requests.post('http://localhost:8000/ai/classify/', json={'user_id': 1, 'food_name': 'apple'}); print('Status:', r.status_code, 'Recommendation:', r.json().get('recommendation'))"
```

#### Test Flutter App
1. Open the app
2. Search for "apple"
3. Add food to log
4. Check recommendations appear

## 🔧 Troubleshooting

### Backend Issues

**Port Already in Use:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn app.main:app --reload --port 8001
```

**Import Errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Database Errors:**
- Delete existing database files
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

### Google Vision API Issues

**Credentials Not Found:**
- Verify file exists: `analog-reef-470415-q6-b8ddae1e11b3.json`
- Check file path in environment variable
- Ensure file has proper JSON format

**API Quota Exceeded:**
- Check Google Cloud Console for quota limits
- Enable billing if required
- Use local fallback database (already implemented)

## 📁 Project Structure

```
Proj fast_api - Copy (3)/
├── app/                    # FastAPI backend
│   ├── ai/                # AI routes and services
│   ├── ai_pipeline/       # AI processing pipeline
│   ├── services/          # Food search and services
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic schemas
│   └── main.py           # FastAPI app entry point
├── nutrition_app/         # Flutter mobile app
│   ├── lib/              # Dart source code
│   └── pubspec.yaml      # Flutter dependencies
├── tests/                # Test files
├── scripts/              # Utility scripts
├── data/                # Data storage (gitignored)
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## 🔐 Security Notes

- ✅ Credentials file is in `.gitignore`
- ✅ Database files are in `.gitignore`
- ✅ `.env` file is in `.gitignore`
- ⚠️ Never commit sensitive files
- ⚠️ Use environment variables for secrets

See `SECURITY.md` for detailed security guidelines.

## 🎯 Key Features

- **Food Search**: Search OpenFoodFacts API with local fallback
- **AI Recommendations**: Intelligent food recommendations based on nutrition
- **User Profiles**: Manage user data and goals
- **Food Logging**: Track daily nutrition intake
- **Image Recognition**: Identify foods from images (Google Vision API)

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review `README.md` for API documentation
3. Check `SECURITY.md` for security concerns
4. Create an issue on GitHub (if repository is public)

## ✅ Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Flutter SDK installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from `.env.example`
- [ ] Google Cloud credentials file in place
- [ ] Database initialized (`python app/create_tables.py`)
- [ ] Backend running (`uvicorn app.main:app --reload`)
- [ ] Flutter dependencies installed (`flutter pub get`)
- [ ] Flutter app running (`flutter run`)
- [ ] API tested and working
- [ ] App tested and working

---

**Your project is now ready to use!** 🎉

