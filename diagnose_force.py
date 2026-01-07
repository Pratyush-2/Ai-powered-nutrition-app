import requests
import sys
import os
sys.path.append(os.getcwd())
try:
    from app import auth, models
    from app.database import SessionLocal
    # Forge Token for user
    db = SessionLocal()
    user = db.query(models.UserProfile).first()
    if not user:
        print("No user found for auth test!")
        TOKEN = "BAD_TOKEN"
    else:
        TOKEN = auth.create_access_token(data={"sub": user.email})
    db.close()
except:
    TOKEN = "BAD_TOKEN"

BASE = "http://127.0.0.1:8000"

def test(name, url, headers={}):
    print(f"Testing {name} ({url})...", end=" ")
    try:
        r = requests.get(url, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code != 200:
            print(f"   Response: {r.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

test("1. Ping", f"{BASE}/debug/1_ping")
test("2. DB", f"{BASE}/debug/2_db")
test("3. Auth", f"{BASE}/debug/3_auth", headers={"Authorization": f"Bearer {TOKEN}"})
