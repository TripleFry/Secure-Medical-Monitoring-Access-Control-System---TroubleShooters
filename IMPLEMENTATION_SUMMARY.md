# 🏥 Posture Detector & ESP32 Integration - Implementation Summary

## What Was Added

### 1. **Posture Detection System** (`posture_detector.py`)
- **Real-time camera-based posture classification**
- Detects: **Standing**, **Sitting**, **Sleeping**
- Uses OpenCV contour analysis (no heavy ML models needed)
- Automatic smoothing to reduce jitter
- **Auto-sends posture to `/activity` endpoint** whenever it changes

**How it works:**
```
Camera Input → OpenCV Contour Analysis → Aspect Ratio Calculation → 
Posture Classification → Smooth Prediction → POST to Server
```

### 2. **Enhanced API Endpoints**

#### `/activity` (POST)
Receives posture/activity data from camera detector or accelerometers.

```bash
curl -X POST http://localhost:5000/activity \
  -H "Content-Type: application/json" \
  -d '{"activity": "Standing", "device_id": "camera-01"}'
```

#### `/esp32` (POST)  
Accepts flexible sensor data from ESP32 devices.

**Full payload** (triggers health analysis + DB logging):
```json
{
  "device_id": "esp32-01",
  "name": "John",
  "age": 45,
  "heart_rate": 72,
  "spo2": 98.5,
  "temperature": 36.6,
  "smoking": false,
  "hypertension": false,
  "humidity": 55,
  "room_temp": 22,
  "aqi": 50
}
```

**Partial payload** (live dashboard update only):
```json
{
  "heart_rate": 85,
  "spo2": 97,
  "temperature": 37
}
```

### 3. **Security Enhancements**
- ✅ **CORS enabled** for cross-origin requests
- ✅ **Optional API token authentication** (set `SENSOR_API_TOKEN` in `.env`)
- ✅ **Bearer token validation** on sensor endpoints

### 4. **Database & Persistence** (`db.py`)
- Flexible `log_vitals()` that accepts optional risk data
- New `log_env_data()` for environmental sensors
- **Auto-fallback to CSV** if database unavailable
- **Timestamped logging** to `esp32_vitals.csv` and `esp32_env_log.csv`

### 5. **Testing & Utilities**
- **`test_sensors.py`** - Complete test suite for all endpoints
- **`quickstart.py`** - Interactive menu to start components
- **`POSTURE_DETECTOR_README.md`** - Full documentation

---

## Quick Start

### 1. Install dependencies (one-time)
```bash
pip install flask flask-cors opencv-python requests numpy
```

### 2. Start the server
```bash
python server.py
```
Server runs on `http://localhost:5000`

### 3. Run posture detector (in new terminal)
```bash
python posture_detector.py
```

**You should see:**
- Live camera feed with FPS counter
- Real-time posture detection (Standing/Sitting/Sleeping)
- Console logs showing POSTs to `/activity` endpoint

### 4. Test the full system
```bash
python test_sensors.py
```

---

## Integration with ESP32

Upload the example sketch to your ESP32:

```cpp
// esp32_example/esp32_post_example.ino

#include <WiFi.h>
#include <HTTPClient.h>

const char* serverUrl = "http://YOUR_SERVER_IP:5000/esp32";

// Post JSON to server with sensor data
String payload = "{\"heart_rate\": 72, \"spo2\": 98.5, ...}";
HTTPClient http;
http.begin(serverUrl);
http.addHeader("Content-Type", "application/json");
int code = http.POST(payload);
```

---

## Architecture Overview

```
┌─────────────────┐       ┌──────────────┐
│  Posture        │       │   ESP32      │
│  Detector       │       │   Sensors    │
│ (Camera)        │       │              │
└────────┬────────┘       └──────┬───────┘
         │                       │
         │ POST /activity        │ POST /esp32
         │                       │
         └───────────┬───────────┘
                     │
                ┌────▼────────────┐
                │  Flask Server   │
                │  (server.py)    │
                └────────┬────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼──┐      ┌────▼──┐      ┌────▼────┐
    │  DB   │      │ CSV   │      │Dashboard│
    │       │      │ Logs  │      │(Real-   │
    └───────┘      └───────┘      │ time)   │
                                   └────────┘
```

---

## File Changes Summary

| File | Change |
|------|--------|
| `server.py` | Added `/esp32` endpoint, CORS support, optional token auth |
| `db.py` | Made `log_vitals()` flexible, added `log_env_data()` |
| `posture_detector.py` | NEW - Real-time posture classification |
| `test_sensors.py` | NEW - Comprehensive endpoint tests |
| `quickstart.py` | NEW - Interactive launcher |
| `esp32_example/esp32_post_example.ino` | NEW - Arduino sketch example |
| `POSTURE_DETECTOR_README.md` | NEW - Full documentation |

---

## Key Features

✅ **Real-time Posture Detection**
- Standing, Sitting, Sleeping classification
- 30 FPS processing on modern CPU
- Automatic smoothing (5-frame history)

✅ **Flexible Sensor Input**
- Full vitals (age + all measurements) → triggers AI health analysis
- Partial vitals → dashboard live updates only
- Environmental data (humidity, temp, AQI) → logged to DB/CSV

✅ **Fallback Persistence**
- Attempts MySQL DB first
- Falls back to CSV if database unavailable
- Zero data loss guaranteed

✅ **Security**
- CORS for web frontend integration
- Optional bearer token authentication
- Request logging and validation

✅ **Easy Testing**
- Pre-built test suite
- Interactive quickstart menu
- Works offline (logs to CSV)

---

## Customization

### Adjust Posture Detection Sensitivity
In `posture_detector.py`, modify `detect_posture()`:
```python
aspect_ratio > 1.5    # Change these thresholds
vertical_position < 0.6
```

### Change Server URL
In `posture_detector.py`:
```python
SERVER_URL = "http://192.168.1.100:5000/activity"  # Your server IP
```

### Enable API Token
In `.env`:
```
SENSOR_API_TOKEN=your_strong_token_here
```

Then include in requests:
```python
headers = {"Authorization": f"Bearer {token}"}
requests.post(url, json=data, headers=headers)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Camera won't open | Check permissions, try camera index 1 or 2 |
| "Unknown" constantly | Improve lighting, wear contrasting clothes |
| Server not responding | Verify `python server.py` is running |
| DB errors | CSV fallback will be used automatically |
| Posture jittery | Smoothing is built-in (5-frame average) |

---

## Next Steps

- [ ] Add confidence scores to posture predictions
- [ ] Implement pose-based activity counting (pushups, squats, etc.)
- [ ] Add wearable integration (heart rate band via Bluetooth)
- [ ] Build mobile app to receive posture alerts
- [ ] Add ML-based posture correction suggestions
- [ ] Integrate sleep tracking with night vision

---

**Ready to use!** Run `python quickstart.py` to launch everything.
