import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_login_flow():
    session = requests.Session()
    
    # 1. Login
    print("--- 1. Logging in ---")
    login_url = f"{BASE_URL}/api/admin/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = session.post(login_url, json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print("Login failed!")
            return
            
        print("Cookies:", session.cookies.get_dict())
        
    except Exception as e:
        print(f"Login Error: {e}")
        return

    # 2. Check Auth
    print("\n--- 2. Checking Auth ---")
    check_auth_url = f"{BASE_URL}/api/check-auth"
    try:
        response = session.get(check_auth_url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Check Auth Error: {e}")

    # 3. Get Members
    print("\n--- 3. Getting Members ---")
    members_url = f"{BASE_URL}/api/members?page=1&pageSize=10"
    try:
        response = session.get(members_url)
        print(f"Status Code: {response.status_code}")
        # Print first 100 chars to avoid spam
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Get Members Error: {e}")

if __name__ == "__main__":
    test_login_flow()
