# Posture Detector & Sensor Integration Guide

## Overview

This system integrates:
1. **Posture Detector** - Real-time camera-based detection of Standing/Sitting/Sleeping
2. **ESP32 Sensor Integration** - Direct POST of vital signs and environmental data
3. **Activity Tracking** - Posture updates feed into dashboard and health analysis

---

## Installation

### 1. Install Dependencies

```bash
pip install flask flask-cors opencv-python requests numpy
```

### 2. Optional: Set API Token (for security)

Edit `.env`:
```
SENSOR_API_TOKEN=your_secure_token_here
```

If not set, endpoints accept unauthenticated requests.

---

## Running the System

### 1. Start the Flask Server

```bash
python server.py
```

Server runs on `http://localhost:5000`

### 2. Run Posture Detector (Camera-based)

In a **separate terminal**:

```bash
python posture_detector.py
```

**Output:**
- Live camera feed with pose skeleton overlay
- Real-time posture classification: Standing/Sitting/Sleeping
- Automatic POST to `/activity` endpoint when posture changes
- Console logs of sent data

**Controls:**
- Press `q` to exit

---

## Endpoints

### `/activity` (POST)
Receive posture/activity data from detector or external sources.

**Request:**
```json
{
  "activity": "Standing",
  "device_id": "camera-01",
  "timestamp": "2026-02-08T10:30:45.123456"
}
```

**Valid activities:** `Standing`, `Sitting`, `Sleeping`, `Unknown`

**Response:**
```json
{
  "status": "success",
  "activity": "Standing"
}
```

---

### `/esp32` (POST)
Full vitals and environmental sensor data from ESP32.

**Full Payload (triggers AI health analysis):**
```json
{
  "device_id": "esp32-01",
  "name": "John Doe",
  "age": 45,
  "gender": "Male",
  "heart_rate": 72,
  "spo2": 98.5,
  "temperature": 36.6,
  "smoking": false,
  "hypertension": false,
  "weight": 80,
  "height": 1.75,
  "humidity": 55,
  "room_temp": 22,
  "aqi": 50
}
```

**Partial Payload (dashboard update only):**
```json
{
  "device_id": "esp32-01",
  "heart_rate": 85,
  "spo2": 97.0,
  "temperature": 37.0
}
```

**Response (Full):**
```json
{
  "status": "ok",
  "risk": "Low",
  "advice": "Your vitals are normal. Continue regular monitoring."
}
```

**Response (Partial):**
```json
{
  "status": "ok",
  "message": "partial data accepted"
}
```

---

## ESP32 Implementation

See `esp32_example/esp32_post_example.ino` for a complete Arduino sketch.

**Key setup:**
```cpp
const char* serverUrl = "http://YOUR_SERVER_IP:5000/esp32";
HTTPClient http;
http.begin(serverUrl);
http.addHeader("Content-Type", "application/json");

String payload = "{\"heart_rate\": 72, \"spo2\": 98.5, \"temperature\": 36.6, ...}";
int code = http.POST(payload);
```

---

## Testing

Run the test suite:

```bash
python test_sensors.py
```

This tests:
- `/activity` endpoint with Standing/Sitting/Sleeping
- `/esp32` endpoint with full and partial payloads
- `/data` endpoint to view current dashboard state

---

## Optional: API Token Security

If `SENSOR_API_TOKEN` is set in `.env`, all sensor endpoints require:

```bash
curl -X POST http://localhost:5000/activity \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"activity": "Standing", "device_id": "camera-01"}'
```

ESP32 and Python requests:
```python
headers = {"Authorization": f"Bearer {api_token}"}
requests.post(url, json=payload, headers=headers)
```

---

## Database Persistence

- **Full vitals** → `vitals_log` table (with risk analysis)
- **Partial vitals** → `esp32_vitals.csv` (fallback if DB unavailable)
- **Environmental** → `env_log` table or `esp32_env_log.csv`
- **Posture** → Updates engine state in real-time

---

## Troubleshooting

### Posture Detector won't start
- Check camera: `python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'No camera')"`
- Ensure camera permissions are granted (Windows may prompt)
- Try a different camera index if available (change `0` to `1`, `2`, etc. in posture_detector.py)

### "Unknown" posture shown constantly
- The detector uses contour analysis. Ensure good lighting and clear background
- Wear contrasting clothing against the background
- Stand 3-6 feet away from camera for best results
- Adjust threshold value `100` in `detect_posture()` if needed

### Server connection fails
- Ensure server is running: `python server.py`
- Check firewall allows `localhost:5000`
- If on different machine, replace `localhost` with server IP in `posture_detector.py`

### Activity not updating
- Check console logs: `🚶 Activity Update: ...`
- Verify `/activity` endpoint is reachable: `curl http://localhost:5000/data`

---

## Architecture

```
┌─────────────────┐
│ Posture Detector│ (MediaPipe + OpenCV)
│  (posture_      │ 
│   detector.py)  │
└────────┬────────┘
         │ POST /activity
         ▼
    ┌─────────────┐       ┌──────────────┐
    │   Server    │◄─────►│  Dashboard   │
    │ (server.py) │       │  (Real-time) │
    └────┬────────┘       └──────────────┘
         ▲
         │ POST /esp32
    ┌────┴─────────┐
    │    ESP32     │ (sensors)
    │   (Arduino)  │
    └──────────────┘
```

---

## Performance Notes

- **Posture detection**: ~30 FPS on modern CPU/GPU
- **Smoothing**: 5-frame history to reduce jitter
- **Server latency**: <200ms typical
- **DB logging**: Best-effort (falls back to CSV if DB unavailable)

---

## Next Steps

- [ ] Add confidence scores to posture predictions
- [ ] Implement pose-based exercise counting
- [ ] Add heart rate variability (HRV) analysis
- [ ] Integrate sleep duration tracking
- [ ] Add waveform visualization for vitals

