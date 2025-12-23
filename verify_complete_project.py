#!/usr/bin/env python3
"""
Comprehensive project verification script
Checks that all required files and directories are present
"""

import os
import sys
from pathlib import Path

# Color codes for output
GREEN = "[OK]"
RED = "[MISSING]"
YELLOW = "[WARN]"

def check_file(filepath, description, required=True):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"{GREEN} {description}: {filepath}")
        return True
    else:
        if required:
            print(f"{RED} {description}: {filepath} - REQUIRED FILE MISSING!")
        else:
            print(f"{YELLOW} {description}: {filepath} - Optional file not found")
        return False

def check_directory(dirpath, description, required=True):
    """Check if a directory exists"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        file_count = len(list(Path(dirpath).rglob('*')))
        print(f"{GREEN} {description}: {dirpath} ({file_count} items)")
        return True
    else:
        if required:
            print(f"{RED} {description}: {dirpath} - REQUIRED DIRECTORY MISSING!")
        else:
            print(f"{YELLOW} {description}: {dirpath} - Optional directory not found")
        return False

def check_files_in_directory(dirpath, required_files, description):
    """Check for specific files in a directory"""
    print(f"\n  Checking {description}:")
    all_present = True
    for filename in required_files:
        filepath = os.path.join(dirpath, filename)
        if os.path.exists(filepath):
            print(f"    {GREEN} {filename}")
        else:
            print(f"    {RED} {filename} - MISSING")
            all_present = False
    return all_present

def main():
    print("=" * 70)
    print("COMPREHENSIVE PROJECT VERIFICATION")
    print("=" * 70)
    
    checks_passed = 0
    checks_total = 0
    
    # Root level files
    print("\n[ROOT] Checking Root Level Files:")
    root_files = [
        ("requirements.txt", "Python dependencies"),
        ("README.md", "Project README"),
        ("SECURITY.md", "Security documentation"),
        ("SETUP_GUIDE.md", "Setup guide"),
        (".gitignore", "Git ignore file"),
        (".env.example", "Environment template"),
        ("Dockerfile", "Docker configuration"),
        ("docker-compose.yml", "Docker Compose"),
        ("alembic.ini", "Database migrations config"),
    ]
    
    for filename, desc in root_files:
        checks_total += 1
        if check_file(filename, desc):
            checks_passed += 1
    
    # Backend App Structure
    print("\n[BACKEND] Checking Backend Structure:")
    backend_dirs = [
        ("app", "Main app directory"),
        ("app/ai", "AI routes and services"),
        ("app/ai_pipeline", "AI processing pipeline"),
        ("app/services", "Service modules"),
        ("app/models", "Model files directory"),
        ("app/routers", "API routers"),
    ]
    
    for dirname, desc in backend_dirs:
        checks_total += 1
        if check_directory(dirname, desc):
            checks_passed += 1
    
    # Critical Backend Files
    print("\n[BACKEND FILES] Checking Critical Backend Files:")
    backend_files = [
        ("app/__init__.py", "App init"),
        ("app/main.py", "FastAPI main entry"),
        ("app/models.py", "Database models"),
        ("app/schemas.py", "Pydantic schemas"),
        ("app/crud.py", "CRUD operations"),
        ("app/database.py", "Database configuration"),
        ("app/config.py", "App configuration"),
        ("app/ai/__init__.py", "AI module init"),
        ("app/ai/ai_routes.py", "AI API routes"),
        ("app/ai/llm_integration.py", "LLM integration"),
        ("app/ai/retriever.py", "RAG retriever"),
        ("app/ai_pipeline/nutrition_engine.py", "Nutrition engine"),
        ("app/ai_pipeline/enhanced_image_recognition.py", "Image recognition"),
        ("app/services/food_search.py", "Food search service"),
    ]
    
    for filepath, desc in backend_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # Flutter App Structure
    print("\n[FLUTTER] Checking Flutter App Structure:")
    flutter_dirs = [
        ("nutrition_app", "Flutter app root"),
        ("nutrition_app/lib", "Dart source code"),
        ("nutrition_app/lib/models", "Data models"),
        ("nutrition_app/lib/services", "API services"),
        ("nutrition_app/lib/screens", "App screens"),
        ("nutrition_app/lib/widgets", "Reusable widgets"),
        ("nutrition_app/android", "Android configuration"),
        ("nutrition_app/ios", "iOS configuration"),
    ]
    
    for dirname, desc in flutter_dirs:
        checks_total += 1
        if check_directory(dirname, desc):
            checks_passed += 1
    
    # Critical Flutter Files
    print("\n[FLUTTER FILES] Checking Critical Flutter Files:")
    flutter_files = [
        ("nutrition_app/pubspec.yaml", "Flutter dependencies"),
        ("nutrition_app/lib/main.dart", "Flutter main entry"),
        ("nutrition_app/lib/models/food.dart", "Food model"),
        ("nutrition_app/lib/services/api_service.dart", "API service"),
        ("nutrition_app/lib/widgets/meal_card_with_recommendation.dart", "Meal card widget"),
    ]
    
    for filepath, desc in flutter_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # Test Structure
    print("\n[TESTS] Checking Test Structure:")
    checks_total += 1
    if check_directory("tests", "Test directory"):
        checks_passed += 1
        # Check for test files
        test_files = [
            "tests/conftest.py",
            "tests/test_crud_ops.py",
            "tests/test_db_connection.py",
            "tests/test_main_endpoints.py",
        ]
        for test_file in test_files:
            checks_total += 1
            if check_file(test_file, f"Test file: {os.path.basename(test_file)}", required=False):
                checks_passed += 1
    
    # Scripts
    print("\n[SCRIPTS] Checking Scripts:")
    checks_total += 1
    if check_directory("scripts", "Scripts directory"):
        checks_passed += 1
    
    # Data Directory
    print("\n[DATA] Checking Data Directory:")
    checks_total += 1
    if check_directory("data", "Data directory", required=False):
        checks_passed += 1
    
    # Check git tracking
    print("\n[GIT] Checking Git Status:")
    try:
        import subprocess
        result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
        tracked_files = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        print(f"{GREEN} Files tracked in git: {tracked_files}")
        checks_passed += 1
        checks_total += 1
    except:
        print(f"{YELLOW} Could not check git status")
        checks_total += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"VERIFICATION SUMMARY: {checks_passed}/{checks_total} checks passed")
    print("=" * 70)
    
    if checks_passed == checks_total:
        print(f"\n{GREEN} ALL CHECKS PASSED! Your project is complete.")
        return 0
    else:
        missing = checks_total - checks_passed
        print(f"\n{YELLOW} {missing} check(s) failed. Review the output above.")
        print("Some files may be optional or generated at runtime.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


