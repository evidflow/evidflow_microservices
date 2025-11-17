#!/usr/bin/env python3
import requests
import json

def test_verification_email():
    print("🧪 Testing Verification Email")
    print("=============================")
    
    test_email = "petergatitu61@gmail.com"
    verification_code = "789123"  # Example verification code
    
    try:
        # First check service health
        print("1. Checking service health...")
        health_response = requests.get("http://localhost:8010/health")
        print(f"   ✅ Health: HTTP {health_response.status_code}")
        health_data = health_response.json()
        print(f"   📧 From: {health_data.get('from_email', 'N/A')}")
        
        # Send verification email
        print(f"2. Sending verification email to {test_email}...")
        verification_response = requests.post(
            "http://localhost:8010/send-verification",
            json={
                "email": test_email,
                "code": verification_code
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   📨 Response: HTTP {verification_response.status_code}")
        if verification_response.status_code == 200:
            print(f"   ✅ Success: {verification_response.json()}")
            print("   📧 Check petergatitu61@gmail.com for the verification email!")
            print(f"   🔑 Verification code: {verification_code}")
        else:
            print(f"   ❌ Error: {verification_response.text}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timeout")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")

if __name__ == "__main__":
    test_verification_email()
