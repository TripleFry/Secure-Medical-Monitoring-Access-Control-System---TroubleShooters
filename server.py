from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash, Response
from flask_cors import CORS
from event_engine import EventEngine
from health_agent import HealthAgent
from clinical_agent import ClinicalAgent
from whatsapp_agent import WhatsAppAgent
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from dotenv import load_dotenv
from db import get_or_create_patient, log_vitals, get_connection
from datetime import datetime
import json

# =============================
# AUTH IMPORT
# =============================
try:
    from auth import (
        create_users_table, create_user, authenticate_user,
        get_user_by_email, verify_user_token
    )
    AUTH_ENABLED = True
    try:
        create_users_table()
        print("✓ Users table initialized")
    except Exception:
        AUTH_ENABLED = False
except ImportError:
    AUTH_ENABLED = False

# =============================
# APP SETUP
# =============================
load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.before_request
def log_request_info():
    print(f"[REQUEST] {request.method} {request.path} from {request.remote_addr}")

# =============================
# COMPONENTS
# =============================
engine = EventEngine()

health_agent = HealthAgent(
    model_path="model.pkl",
    scaler_path="scaler.pkl"
)

API_KEY = os.getenv("GROQ_API_KEY")
clinical_agent = ClinicalAgent(API_KEY)

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_WHATSAPP_NUMBER")
TWILIO_TO = os.getenv("DOCTOR_WHATSAPP_NUMBER")

whatsapp_agent = WhatsAppAgent(
    TWILIO_SID,
    TWILIO_TOKEN,
    TWILIO_FROM,
    TWILIO_TO
)

# ============================================================
# AUTH ROUTES
# ============================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if AUTH_ENABLED:
            result = authenticate_user(email, password)
            if result["success"]:
                session["logged_in"] = True
                session["user_email"] = email
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error="Invalid credentials")
        else:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        role = request.form.get("role")

        if AUTH_ENABLED:
            result = create_user(email, password, fullname, role)
            if result["success"]:
                return render_template("signup.html", success="Account created")
            else:
                return render_template("signup.html", error="Signup failed")
        else:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ============================================================
# FRONTEND ROUTES
# ============================================================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/alerts")
def alerts_page():
    return render_template("alerts.html")

@app.route("/charts")
def charts_page():
    return render_template("charts.html")

# ============================================================
# EVENT ROUTE (intruder etc.)
# ============================================================
@app.route("/event", methods=["POST"])
def receive_event():
    data = request.json
    event_type = data.get("event")

    state = engine.process_event(event_type)

    if event_type == "intruder_detected":
        whatsapp_agent.send_alert(
            "🚨 SECURITY ALERT: Intruder detected in restricted area."
        )

    return jsonify(state)

# ============================================================
# ESP32 DATA ENDPOINT
# ============================================================
@app.route("/esp32", methods=["POST"])
def esp32_post():
    try:
        raw_data = request.json or {}

        data = {}
        for k, v in raw_data.items():
            data[str(k).lower().strip()] = v

        device_id = data.get("device_id", "esp32")

        print(f"[ESP32] Received Data: {data}")

        def get_best_vital(keys):
            best_val = None
            for k in keys:
                val = data.get(k)
                if val is not None:
                    is_zero = (str(val).strip() == "0" or val == 0)
                    is_best_zero = (best_val is None or str(best_val).strip() == "0" or best_val == 0)
                    if best_val is None or (is_best_zero and not is_zero):
                        best_val = val
            return best_val

        heart_rate = get_best_vital(["heart_rate", "hr", "pulse", "bpm"])
        spo2 = get_best_vital(["spo2", "spo", "ox", "oxygen"])
        temperature = get_best_vital(["temperature", "temp", "t"])

        name = "Ramesh Gupta"
        age = 20
        gender = "male"
        smoking = False
        hypertension = False
        weight = 70.0

        humidity = data.get("humidity")
        room_temp = data.get("room_temp")
        aqi = data.get("aqi")
        emergency = data.get("emergency")
        fall = data.get("fall")
        posture = data.get("posture")

        timestamp = datetime.utcnow().isoformat()

        if posture:
            engine.update_activity(posture)

        if humidity is not None or room_temp is not None or aqi is not None:
            engine.update_env_data(
                humidity=humidity or "--",
                room_temp=room_temp or "--",
                aqi=aqi or "--"
            )

        # Emergency alert
        if emergency:
            engine.update_emergency(emergency)
            whatsapp_agent.send_alert(
                f"🆘 EMERGENCY: Help button pressed by {name}!"
            )

        # Fall alert
        if fall:
            engine.update_fall(fall)
            whatsapp_agent.send_alert(
                f"⚠️ FALL detected for {name}! Immediate assistance required."
            )

        # Vitals update
        if heart_rate is not None and spo2 is not None and temperature is not None:
            payload = {
                "age": age,
                "heart_rate": heart_rate,
                "spo2": spo2,
                "temperature": temperature,
                "gender": gender,
                "smoking": smoking,
                "hypertension": hypertension,
                "weight": weight,
                "name": name
            }

            risk_result = health_agent.predict(payload)

            advice = clinical_agent.generate_advice(
                vitals={
                    "age": age,
                    "heart_rate": heart_rate,
                    "spo2": spo2,
                    "temperature": temperature
                },
                risk=risk_result["risk"]
            )

            engine.update_vitals(
                heart_rate=heart_rate,
                spo2=spo2,
                temperature=temperature,
                risk=risk_result["risk"],
                age=age,
                gender=gender,
                smoking=smoking,
                hypertension=hypertension,
                name=name
            )

            # High risk alert
            if risk_result["risk"] == "High":
                whatsapp_agent.send_alert(
                    f"""⚠️ MEDICAL ALERT
Patient: {name}
Status: HIGH RISK

Heart Rate: {heart_rate} bpm
SpO2: {spo2}%
Temperature: {temperature}°C

Advice:
{advice[:500]}"""
                )

            try:
                lookup_payload = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "smoking": smoking,
                    "hypertension": hypertension
                }
                patient_id = get_or_create_patient(lookup_payload)

                vitals_payload = {
                    "heart_rate": heart_rate,
                    "spo2": spo2,
                    "temperature": temperature,
                    "weight": weight
                }

                log_vitals(patient_id, vitals_payload)

            except Exception as db_e:
                print(f"DB Log Error: {db_e}")

        # CSV log
        with open("esp32_sensor_log.csv", "a") as f:
            f.write(f"{timestamp},{device_id},{name},{heart_rate},{spo2},{temperature},{humidity},{room_temp},{aqi}\n")

        print("✨ Sensor data update complete")
        return jsonify({"status": "ok"})

    except Exception as e:
        print(f"💥 ESP32 Endpoint Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================
# DASHBOARD DATA
# ============================================================
@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(engine.state)

# ============================================================
# RUN SERVER
# ============================================================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
