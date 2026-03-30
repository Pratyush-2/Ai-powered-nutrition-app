#!/bin/bash
# Super fast development launcher - runs backend and frontend simultaneously

cd "$(dirname "$0")/.."

# Start FastAPI backend in background
uvicorn app.main:app --reload &

# Start Flutter frontend
flutter run --hot --fast-start
