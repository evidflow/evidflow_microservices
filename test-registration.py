#!/usr/bin/env python3
import requests
import json

def test_registration():
    print("🧪 Testing User Registration with Email Verification")
    print("====================================================")
    
    registration_data = {
        "email": "petergatitu61@gmail.com",
        "password": "securepassword123",
        "full_name": "Peter Gatitu"
    }
    
    try:
        # Replace with your actual authentication service URL
        auth_service_url = "http://localhost:8000/register"  # Adjust port if different
        
        print(f"1. Registering user: {registration_data['email']}")
        response = requests.post(
            auth_service_url,
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📨 Response: HTTP {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Registration successful!")
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Message: {result.get('message')}")
            print(f"📧 Verification email should be sent to {registration_data['email']}")
        else:
            print(f"❌ Registration failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_registration()
