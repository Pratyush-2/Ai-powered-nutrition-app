# Nutrition AI Application

A comprehensive AI-powered nutrition application built with FastAPI, featuring Random Forest classification, RAG (Retrieval-Augmented Generation), and LLM integration for intelligent food recommendations and nutritional guidance.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │    │   FastAPI       │    │   AI Pipeline   │
│                 │    │   Backend       │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Food Search   │◄──►│ • REST API      │◄──►│ • OpenFoodFacts │
│ • Recommendations│    │ • User Profiles │    │ • FAISS Index   │
│ • Chat Interface│    │ • Daily Logs    │    │ • Random Forest │
│ • Progress Track│    │ • AI Endpoints  │    │ • LLM Service   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Features

### Core AI Pipeline
- **Data Ingestion**: OpenFoodFacts API integration with intelligent caching
- **Semantic Search**: FAISS-powered vector search for nutrition facts
- **Machine Learning**: Random Forest classifier for food recommendations
- **LLM Integration**: OpenAI/HuggingFace support for natural language explanations
- **Verification**: Automated macro claim verification and correction
- **Monitoring**: Comprehensive analytics and user feedback collection

### API Endpoints
- `GET /ai/get-nutrition-facts/` - Semantic search for nutrition facts
- `POST /ai/classify-food/` - Food recommendation classification
- `POST /ai/generate-explanation/` - Comprehensive AI explanations
- `POST /ai/chat/` - Natural language nutrition chat
- `GET /ai/health/` - Service health monitoring

### Flutter Integration
- Ready-to-use service classes for API integration
- Comprehensive error handling and loading states
- Real-time chat interface with nutrition context
- Food recommendation cards with confidence scores

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+ (for Flutter)
- Git

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Pratyush-2/ai-powered-nutrition-app.git
cd ai-powered-nutrition-app
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required environment variables:
```env
OPENAI_API_KEY=your_openai_api_key_here
HF_API_TOKEN=your_hf_token_here
FAISS_INDEX_PATH=backend/indexes/nutrition.index
EMB_MODEL=all-MiniLM-L6-v2
RF_MODEL_PATH=models/random_forest_model.pkl
DATABASE_URL=sqlite:///./data/app.db
```

### 3. Quick Setup (Recommended)
```bash
# Complete setup with one command
make setup
```

### 4. Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed nutrition database
python backend/ai/fetch_openfoodfacts.py --seed "paneer,apple,banana,spinach,almonds,white rice,chicken breast,dal,yogurt,oats"

# Build FAISS index
python scripts/build_faiss_index.py

# Train Random Forest model
python backend/ai/train_rf.py --jsonl data/nutrition_facts.jsonl
```

## 🚀 Running the Application

### Backend (FastAPI)
```bash
# Using Makefile
make run

# Or directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Flutter App
```bash
cd nutrition_app
flutter pub get
flutter run
```

### Docker (Optional)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Run Specific Test Suites
```bash
# AI endpoint tests
pytest tests/ai/ -v

# Database tests
pytest tests/test_db_connection.py -v

# CRUD operations tests
pytest tests/test_crud_ops.py -v
```

### Demo Script
```bash
# Run complete demo
make demo

# Or manually
bash scripts/demo_run.sh
```

## 📊 API Usage Examples

### 1. Get Nutrition Facts
```bash
curl "http://localhost:8000/ai/get-nutrition-facts/?q=paneer&k=3"
```

### 2. Classify Food
```bash
curl -X POST "http://localhost:8000/ai/classify-food/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "food_name": "paneer", "quantity_g": 100}'
```

### 3. Generate Explanation
```bash
curl -X POST "http://localhost:8000/ai/generate-explanation/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "food_name": "paneer", "quantity_g": 100, "extra_context": "I'\''m trying to build muscle"}'
```

### 4. Chat Interface
```bash
curl -X POST "http://localhost:8000/ai/chat/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "message": "What should I eat for breakfast?", "food_context": null}'
```

## 🔧 Configuration

### Model Parameters
- **Random Forest**: 200 estimators, max depth 12
- **Embeddings**: all-MiniLM-L6-v2 (384 dimensions)
- **FAISS Index**: IndexFlatIP for cosine similarity
- **LLM**: GPT-3.5-turbo with temperature 0.0 (factual) / 0.7 (chat)

### Rate Limiting
- Default: 60 requests per minute per IP
- Configurable via `RATE_LIMIT_PER_MINUTE` environment variable

### Monitoring
- All predictions logged to SQLite database
- User feedback collection for model improvement
- Performance metrics and error tracking
- CSV export for analysis

## 📈 Monitoring & Analytics

### Health Check
```bash
curl "http://localhost:8000/ai/health/"
```

### View Metrics
```python
from backend.ai.monitoring import get_monitoring

monitoring = get_monitoring()
metrics = monitoring.get_prediction_metrics(days=7)
print(metrics)
```

### Retrain Model
```bash
# Retrain with user feedback
python scripts/retrain_rf.py

# Or schedule weekly retraining
echo "0 2 * * 0 cd /path/to/project && python scripts/retrain_rf.py" | crontab -
```

## 🏗️ Development

### Project Structure
```
├── app/                    # FastAPI application
│   ├── main.py            # Main application entry point
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   └── crud.py            # Database operations
├── backend/               # AI pipeline
│   └── ai/
│       ├── fetch_openfoodfacts.py  # Data ingestion
│       ├── embeddings.py           # FAISS index management
│       ├── retriever.py            # Semantic search
│       ├── train_rf.py             # Random Forest training
│       ├── rf_model.py             # Model runtime
│       ├── llm_service.py          # LLM integration
│       ├── verifier.py             # Claim verification
│       ├── ai_routes.py            # API endpoints
│       └── monitoring.py           # Analytics
├── nutrition_app/         # Flutter application
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docs/                  # Documentation
└── data/                  # Data storage
```

### Adding New Features

1. **New AI Models**: Add to `backend/ai/` directory
2. **New Endpoints**: Add to `backend/ai/ai_routes.py`
3. **New Tests**: Add to `tests/ai/` directory
4. **New Documentation**: Add to `docs/` directory

### Code Quality
```bash
# Run linting
flake8 app/ backend/ tests/

# Format code
black app/ backend/ tests/

# Type checking
mypy app/ backend/
```

## 🚀 Deployment

### Production Checklist
- [ ] Set up proper authentication
- [ ] Configure production database
- [ ] Set up monitoring and alerting
- [ ] Configure rate limiting
- [ ] Set up SSL certificates
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

### Environment Variables
```env
# Production settings
DATABASE_URL=postgresql://user:pass@localhost/nutrition_db
OPENAI_API_KEY=your_production_key
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenFoodFacts](https://world.openfoodfacts.org/) for nutrition data
- [Hugging Face](https://huggingface.co/) for embedding models
- [OpenAI](https://openai.com/) for language models
- [FAISS](https://github.com/facebookresearch/faiss) for vector search
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Flutter](https://flutter.dev/) for the mobile framework

## 📞 Support

For support, email support@nutrition-ai.com or create an issue on GitHub.

## 🔮 Roadmap

- [ ] Graph Neural Networks for food recommendations
- [ ] Causal uplift ranking for personalized suggestions
- [ ] Reinforcement learning for user preference learning
- [ ] Multi-modal input (images, voice)
- [ ] Real-time nutrition tracking
- [ ] Social features and sharing
- [ ] Integration with fitness trackers
- [ ] Advanced meal planning algorithms

---

**Made with ❤️ for better nutrition and health**

