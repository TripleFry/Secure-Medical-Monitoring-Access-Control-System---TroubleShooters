#!/usr/bin/env python3
"""
Quick Start Guide for Posture Detector + ESP32 Integration
Run this to launch all components with proper sequence
"""

import subprocess
import time
import os
import sys
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent

print("""
╔════════════════════════════════════════════════════════════╗
║     Health Monitoring System - Posture Detector & ESP32   ║
╚════════════════════════════════════════════════════════════╝

This script will:
1. Start Flask Server (http://localhost:5000)
2. Launch Posture Detector (uses webcam)
3. Optionally run sensor tests

""")

# Check dependencies
print("📦 Checking dependencies...")
try:
    import flask
    import cv2
    import requests
    import numpy
    print("✅ All dependencies installed\n")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\nInstall with: pip install flask flask-cors opencv-python requests numpy")
    sys.exit(1)

# Menu
print("Choose what to run:")
print("1. Start Server Only")
print("2. Start Server + Posture Detector")
print("3. Run Tests Only (server must be running)")
print("4. Quick Test (all-in-one demo)")

choice = input("\nEnter choice (1-4): ").strip()

if choice == "1":
    print("\n🚀 Starting Flask Server...\n")
    subprocess.run(["python", str(project_dir / "server.py")])

elif choice == "2":
    print("\n🚀 Starting Flask Server in background...")
    server_proc = subprocess.Popen(
        ["python", str(project_dir / "server.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)  # Wait for server to start
    
    print("🎥 Starting Posture Detector...\n")
    try:
        subprocess.run(["python", str(project_dir / "posture_detector.py")])
    except KeyboardInterrupt:
        print("\n👋 Stopping detector...")
    finally:
        server_proc.terminate()
        print("✓ Server stopped")

elif choice == "3":
    print("\n🧪 Running Test Suite...\n")
    subprocess.run(["python", str(project_dir / "test_sensors.py")])

elif choice == "4":
    print("\n🎯 Starting Full Demo (Server + Tests)...\n")
    print("🚀 Starting Server...")
    server_proc = subprocess.Popen(
        ["python", str(project_dir / "server.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    
    print("✓ Server ready\n")
    print("🧪 Running test suite...\n")
    result = subprocess.run(["python", str(project_dir / "test_sensors.py")])
    
    server_proc.terminate()
    print("\n✓ Demo complete")

else:
    print("Invalid choice")
    sys.exit(1)
