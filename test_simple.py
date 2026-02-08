#!/usr/bin/env python3
"""
Simple test for posture detector and sensor integration (no emojis for Windows compatibility).
Run the Flask server first, then run this script to test both endpoints.
"""

import requests
import json
from datetime import datetime
import time

SERVER_URL = "http://localhost:5000"

def test_activity_endpoint():
    """Test the /activity endpoint with posture data"""
    print("\n[TEST] Testing /activity Endpoint")
    print("=" * 50)
    
    test_cases = [
        {"activity": "Standing", "device_id": "camera-01"},
        {"activity": "Sitting", "device_id": "camera-01"},
        {"activity": "Sleeping", "device_id": "camera-01"},
    ]
    
    for payload in test_cases:
        try:
            response = requests.post(
                f"{SERVER_URL}/activity",
                json=payload,
                timeout=5
            )
            print(f"\nActivity: {payload['activity']}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"[ERROR] Error sending {payload['activity']}: {e}")


def test_esp32_endpoint():
    """Test the /esp32 endpoint with sensor data"""
    print("\n\n[TEST] Testing /esp32 Endpoint")
    print("=" * 50)
    
    test_cases = [
        # Full vitals payload (triggers health analysis)
        {
            "device_id": "esp32-01",
            "name": "John Doe",
            "age": 45,
            "gender": "Male",
            "heart_rate": 72,
            "spo2": 98.5,
            "temperature": 36.6,
            "smoking": False,
            "hypertension": False,
            "weight": 80,
            "height": 1.75,
            "humidity": 55,
            "room_temp": 22,
            "aqi": 50
        },
        # Partial vitals (dashboard update only)
        {
            "device_id": "esp32-01",
            "name": "Alice",
            "heart_rate": 85,
            "spo2": 97.0,
            "temperature": 37.0,
            "humidity": 60
        }
    ]
    
    for i, payload in enumerate(test_cases):
        try:
            print(f"\nTest Case {i+1}:")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{SERVER_URL}/esp32",
                json=payload,
                timeout=5
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"[ERROR] Error: {e}")
        
        time.sleep(1)


def test_data_endpoint():
    """Fetch current dashboard state"""
    print("\n\n[TEST] Testing /data Endpoint (Dashboard State)")
    print("=" * 50)
    
    try:
        response = requests.get(f"{SERVER_URL}/data", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Current State:\n{json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def main():
    print("[INFO] Sensor Integration Test Suite")
    print(f"[INFO] Server: {SERVER_URL}")
    print("\n[INFO] Make sure Flask server is running: python server.py")
    
    try:
        # Quick health check
        response = requests.get(f"{SERVER_URL}/data", timeout=2)
        print("[OK] Server is reachable\n")
    except Exception as e:
        print(f"[ERROR] Server is not reachable: {e}")
        print("[INFO] Please start the server first: python server.py")
        return
    
    # Run tests
    test_activity_endpoint()
    test_esp32_endpoint()
    test_data_endpoint()
    
    print("\n\n[DONE] Test suite complete!")


if __name__ == "__main__":
    main()
