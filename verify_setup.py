#!/usr/bin/env python3
"""
Verification script to ensure project setup is correct
"""

import sys
import os

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[FAIL] {description}: {filepath} - NOT FOUND")
        return False

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"[OK] {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"[FAIL] {description}: {module_name} - {e}")
        return False

def main():
    print("Verifying Project Setup...\n")
    
    checks_passed = 0
    checks_total = 0
    
    # Check critical files
    print("[FILES] Checking Critical Files:")
    checks_total += 1
    if check_file_exists("app/main.py", "FastAPI main file"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("app/ai/ai_routes.py", "AI routes"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("app/services/food_search.py", "Food search service"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("requirements.txt", "Python dependencies"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists(".gitignore", "Git ignore file"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists(".env.example", "Environment template"):
        checks_passed += 1
    
    # Check security files (should exist but not be tracked)
    print("\n[SECURITY] Checking Security:")
    checks_total += 1
    credentials_file = "analog-reef-470415-q6-b8ddae1e11b3.json"
    if os.path.exists(credentials_file):
        print(f"[OK] Google Cloud credentials file exists: {credentials_file}")
        # Check if it's in .gitignore
        try:
            with open(".gitignore", "r") as f:
                gitignore_content = f.read()
                if credentials_file in gitignore_content:
                    print(f"[OK] Credentials file is in .gitignore")
                    checks_passed += 1
                else:
                    print(f"[WARN] Credentials file NOT in .gitignore - ADD IT!")
        except:
            print(f"[WARN] Could not verify .gitignore")
    else:
        print(f"[WARN] Google Cloud credentials file not found: {credentials_file}")
        print(f"   (This is OK if you're using environment variables)")
    
    checks_total += 1
    
    # Check imports (only if dependencies are installed)
    print("\n[IMPORTS] Checking Python Imports:")
    try:
        checks_total += 1
        if check_import("fastapi", "FastAPI"):
            checks_passed += 1
        
        checks_total += 1
        if check_import("uvicorn", "Uvicorn"):
            checks_passed += 1
        
        checks_total += 1
        if check_import("sqlalchemy", "SQLAlchemy"):
            checks_passed += 1
        
        checks_total += 1
        if check_import("requests", "Requests"):
            checks_passed += 1
    except:
        print("[WARN] Skipping import checks (dependencies may not be installed)")
    
    # Check Flutter app
    print("\n[FLUTTER] Checking Flutter App:")
    checks_total += 1
    if check_file_exists("nutrition_app/pubspec.yaml", "Flutter pubspec"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("nutrition_app/lib/main.dart", "Flutter main file"):
        checks_passed += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"[SUMMARY] Verification Summary: {checks_passed}/{checks_total} checks passed")
    
    if checks_passed == checks_total:
        print("[SUCCESS] All checks passed! Project setup looks good.")
        return 0
    else:
        print("[WARNING] Some checks failed. Review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

