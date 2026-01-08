# 🗺️ Key Project Files Guide

This guide highlights the most important files in your AI-Powered Nutrition App and explains what they do.

---

## 🧠 AI & Intelligent Features

### 1. Recommendation Engine (The "Decision Maker")
- **File**: `app/ai_pipeline/nutrition_engine.py`
- **Why it's important**: This is the core logic that decides if a food is "Recommended" or "Not Recommended". 
- **Key Features**: 
  - Hard Veto Rules (e.g., "Cake" = Bad)
  - Healthy Fat Bonus (e.g., "Butter" = Good)
  - Sugar Estimation Logic

### 2. Health Safety System (The "Doctor")
- **File**: `app/health_checker.py`
- **Why it's important**: Protects users based on their health profile.
- **Key Features**:
  - **Diabetes**: Detects refined carbs, high sugar, and glycemic risks.
  - **Allergies**: Detects lactose (including hidden dairy), gluten, nuts, etc.

### 3. AI Chat & RAG (The "Assistant")
- **Files**: 
  - `app/ai/llm_integration.py` (Talks to Gemini AI)
  - `app/ai/retriever.py` (The RAG system - retrieves context)
  - `app/ai/ai_routes.py` (API endpoints for chat)
- **Why it's important**: Handles the "Chat with AI" feature, giving it context about nutrition.

---

## 🔙 Backend (FastAPI)

### 1. Search Service (The "Finder")
- **File**: `app/services/food_search.py`
- **Why it's important**:  **CRITICAL**. Handles food searching.
- **Key Features**:
  - Connects to OpenFoodFacts (fetching 50 popular items).
  - Implements the "10,000 point" scoring algorithm (Rice > Rice Krispies).
  - Manages caching and local DB fallback.

### 2. Core Infrastructure
- **File**: `app/main.py` (Entry point, starts the server)
- **File**: `app/models.py` (Database tables: Users, Foods, Logs, Goals)
- **File**: `app/schemas.py` (Data validation rules)

---

## 📱 Frontend (Flutter)

### 1. Main Screens
- **`lib/screens/home_screen.dart`**: Main dashboard & daily summary.
- **`lib/screens/food_search_screen.dart`**: Search interface.
- **`lib/screens/history_screen.dart`**: Food log with **Edit/Delete** and **Daily Totals**.
- **`lib/screens/goals_screen.dart`**: Progress charts with **Weekly Navigation**.

### 2. Connectivity
- **`lib/services/api_service.dart`**: The bridge that talks to your backend. If this breaks, the app stops working.

---

## 📂 Quick Reference for Presentation

| Feature | Files to Show |
|---------|---------------|
| **"Smart Search"** | `app/services/food_search.py` |
| **"Health Warnings"** | `app/health_checker.py` |
| **"Recommendations"** | `app/ai_pipeline/nutrition_engine.py` |
| **"Weekly Graphs"** | `lib/screens/goals_screen.dart` |
| **"AI Chat"** | `app/ai/llm_integration.py` |
