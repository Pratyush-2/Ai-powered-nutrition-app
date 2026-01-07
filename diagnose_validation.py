import requests
try:
    resp = requests.get("http://127.0.0.1:8000/whoami")
    print(f"Connected to: {resp.text}")
except Exception as e:
    print(f"Failed: {e}")
