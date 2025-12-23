"""
Comprehensive API Endpoint Testing Script
"""
import requests
import json
from datetime import date, datetime

BASE_URL = "http://127.0.0.1:8000"

def main():
    print('\n' + '='*60)
    print('  TESTING NUTRITION API ENDPOINTS')
    print('='*60)

    # Test 1: Register
    print('\n[1] Testing POST /auth/register...')
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_user = {
        'email': f'test_{timestamp}@example.com',
        'password': 'testpassword123',
        'name': 'Test User',
        'age': 30,
        'weight_kg': 70.0,
        'height_cm': 175.0,
        'gender': 'male',
        'activity_level': 'medium',
        'goal': 'maintain'
    }
    try:
        response = requests.post(f'{BASE_URL}/auth/register', json=test_user)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            print('✅ Registration successful')
        else:
            print(f'❌ Failed: {response.text[:200]}')
            return
    except Exception as e:
        print(f'❌ Error: {e}')
        return

    # Test 2: Login
    print('\n[2] Testing POST /auth/login...')
    try:
        login_data = {'username': test_user['email'], 'password': test_user['password']}
        response = requests.post(f'{BASE_URL}/auth/login', data=login_data)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            token = response.json()['access_token']
            print(f'✅ Login successful, token: {token[:20]}...')
        else:
            print(f'❌ Failed: {response.text[:200]}')
            return
    except Exception as e:
        print(f'❌ Error: {e}')
        return

    headers = {'Authorization': f'Bearer {token}'}

    # Test 3: Get Profile
    print('\n[3] Testing GET /profiles/me...')
    try:
        response = requests.get(f'{BASE_URL}/profiles/me', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            print(f'✅ Profile retrieved: {response.json()["name"]}')
        else:
            print(f'❌ Failed: {response.text[:200]}')
    except Exception as e:
        print(f'❌ Error: {e}')

    # Test 4: Create Food
    print('\n[4] Testing POST /foods/...')
    test_food = {'name': 'Test Apple', 'calories': 52.0, 'protein': 0.3, 'carbs': 14.0, 'fats': 0.2}
    try:
        response = requests.post(f'{BASE_URL}/foods/', json=test_food, headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            food_id = response.json()['id']
            print(f'✅ Food created with ID: {food_id}')
        else:
            print(f'❌ Failed: {response.text[:200]}')
            food_id = None
    except Exception as e:
        print(f'❌ Error: {e}')
        food_id = None

    # Test 5: Create Goal
    print('\n[5] Testing POST /goals/...')
    test_goal = {'calories_goal': 2000.0, 'protein_goal': 150.0, 'carbs_goal': 200.0, 'fats_goal': 65.0}
    try:
        response = requests.post(f'{BASE_URL}/goals/', json=test_goal, headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            print(f'✅ Goal created successfully')
        else:
            print(f'❌ Failed: {response.text[:200]}')
    except Exception as e:
        print(f'❌ Error: {e}')

    # Test 6: Get Goals
    print('\n[6] Testing GET /goals/...')
    try:
        response = requests.get(f'{BASE_URL}/goals/', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            goals = response.json()
            print(f'✅ Retrieved {len(goals)} goal(s)')
        else:
            print(f'❌ Failed: {response.text[:200]}')
    except Exception as e:
        print(f'❌ Error: {e}')

    # Test 7: Create Log
    if food_id:
        print('\n[7] Testing POST /logs/...')
        log_data = {'food_id': food_id, 'quantity': 1.5, 'date': date.today().isoformat()}
        try:
            response = requests.post(f'{BASE_URL}/logs/', json=log_data, headers=headers)
            print(f'Status: {response.status_code}')
            if response.status_code == 200:
                log_id = response.json()['id']
                print(f'✅ Log created with ID: {log_id}')
            else:
                print(f'❌ Failed: {response.text[:200]}')
                log_id = None
        except Exception as e:
            print(f'❌ Error: {e}')
            log_id = None
    else:
        print('\n[7] Skipping log test - no food_id')
        log_id = None

    # Test 8: Get Totals
    print('\n[8] Testing GET /totals/{date}...')
    try:
        response = requests.get(f'{BASE_URL}/totals/{date.today().isoformat()}', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            totals = response.json()
            print(f'✅ Totals: calories={totals["calories"]}, protein={totals["protein"]}')
        else:
            print(f'❌ Failed: {response.text[:200]}')
    except Exception as e:
        print(f'❌ Error: {e}')

    # Test 9: Get Logs
    print('\n[9] Testing GET /logs/...')
    try:
        response = requests.get(f'{BASE_URL}/logs/', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            logs = response.json()
            print(f'✅ Retrieved {len(logs)} log(s)')
        else:
            print(f'❌ Failed: {response.text[:200]}')
    except Exception as e:
        print(f'❌ Error: {e}')

    print('\n' + '='*60)
    print('  TESTING COMPLETE')
    print('='*60 + '\n')

if __name__ == "__main__":
    main()
