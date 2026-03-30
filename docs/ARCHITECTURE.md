# Project Architecture

This document provides a high-level overview of the AI-Powered Nutrition App architecture and codebase structure.

## Core System Components

The application adopts a decoupled architecture with a FastAPI backend acting as the central intelligence and data hub, and a Flutter frontend handling client interactions.

### 1. Intelligent Engine (`app/ai_pipeline/nutrition_engine.py`)
The decision-making component of the pipeline. It replaces simple rule-based classification with an ML-capable evaluation model:
- Implements comprehensive veto rules (e.g., specific allergen triggers).
- Handles positive reinforcement weighting (e.g., healthy fat ratios).
- Computes estimated health metrics (like added sugar approximation) when OpenFoodFacts returns missing or partial nutritional data.

### 2. Health & Safety Verifier (`app/health_checker.py`)
This module maps user health profiles (e.g., lactose intolerance, diabetes) to parsed food ingredients:
- Evaluates glycemic response risks by analyzing refined carbohydrate content.
- Extracts hidden allergens dynamically (e.g., identifying whey as dairy).

### 3. RAG & LLM Integration
- **Retrieval (`app/ai/retriever.py`)**: Vector search engine that provides semantic context from a FAISS index.
- **Generation (`app/ai/llm_integration.py` & `app/ai/ai_routes.py`)**: Integrates LLMs to provide conversational assistance with the nutrition context appended to prompts.

### 4. Search and Data Aggregation (`app/services/food_search.py`)
The primary gateway for resolving food queries:
- Bridges the internal database with OpenFoodFacts.
- Incorporates a normalized scoring algorithm to prioritize exact matches or whole foods (e.g., ensuring "rice" ranks above "rice cakes").
- Handles fallback and caching layers for latency optimization.

## Frontend (Flutter) Structure

The mobile application is built with Flutter, focusing on state management and modular services.

- `lib/screens/home_screen.dart`: Primary dashboard and macro summary view.
- `lib/screens/food_search_screen.dart`: Interface integrating with the backend search service.
- `lib/screens/history_screen.dart`: Daily log management and historical trend visualization.
- `lib/screens/goals_screen.dart`: Statistical charts predicting weekly/monthly progress based on logged metrics.
- `lib/services/api_service.dart`: The universal API client abstracting all REST calls to the FastAPI backend.
