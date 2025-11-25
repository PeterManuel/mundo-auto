"""
Test script to verify login functionality.
"""
import os
import sys
import requests
import json

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_login():
    """
    Test login functionality by directly calling the API endpoint.
    This helps verify that authentication is working correctly.
    """
    print("Testing login functionality...")
    
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    # Test admin login
    admin_credentials = {
        "username": "admin@mundoauto.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            login_url, 
            data={
                "username": admin_credentials["username"],
                "password": admin_credentials["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin login successful! Token received: {data['access_token'][:20]}...")
        else:
            print(f"❌ Admin login failed with status code: {response.status_code}")
            print(f"Error response: {response.text}")
            
        # Test demo login
        demo_credentials = {
            "username": "demo@mundoauto.com",
            "password": "demo123"
        }
        
        response = requests.post(
            login_url, 
            data={
                "username": demo_credentials["username"],
                "password": demo_credentials["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Demo login successful! Token received: {data['access_token'][:20]}...")
        else:
            print(f"❌ Demo login failed with status code: {response.status_code}")
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing login: {str(e)}")
        print("Make sure the API server is running!")

if __name__ == "__main__":
    test_login()