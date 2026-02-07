from flask import Flask, request, jsonify, render_template
from event_engine import EventEngine
from health_agent import HealthAgent
from clinical_agent import ClinicalAgent
from whatsapp_agent import WhatsAppAgent
import os
from dotenv import load_dotenv
from db import get_or_create_patient, log_vitals
from db import get_connection
from datetime import datetime
from sqlalchemy import text


app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize components
engine = EventEngine()

health_agent = HealthAgent(
    model_path="model.pkl",
    scaler_path="scaler.pkl"
)

# LLM agent
API_KEY = os.getenv("GROQ_API_KEY")
clinical_agent = ClinicalAgent(API_KEY)

# WhatsApp agent
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

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/alerts")
def alerts_page():
    return render_template("alerts.html")




@app.route("/history/<int:patient_id>")
def get_history(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT heart_rate, spo2, temperature, timestamp
        FROM vitals_log
        WHERE patient_id = %s
        ORDER BY timestamp DESC
        LIMIT 20
    """
    cursor.execute(query, (patient_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Reverse so graph goes oldest → newest
    rows.reverse()

    return jsonify(rows)




@app.route("/event", methods=["POST"])
def receive_event():
    data = request.json
    event_type = data.get("event")
    image_path = data.get("image")  # optional intruder image

    # Process event
    state = engine.process_event(event_type, image_path)

    # Intruder WhatsApp alert
    if event_type == "intruder_detected":
        alert_message = """
🚨 SECURITY ALERT

Intruder detected in restricted area.

Immediate action required.
"""
        whatsapp_agent.send_alert(alert_message)

    return jsonify(state)




@app.route("/health", methods=["POST"])
def health_check():
    data = request.json

    # Step 1: ML prediction
    risk_result = health_agent.predict(data)

    # Step 2: LLM reasoning
    vitals_for_llm = {
        "age": data["age"],
        "heart_rate": data["heart_rate"],
        "spo2": data["spo2"],
        "temperature": data["temperature"]
    }

    advice = clinical_agent.generate_advice(
        vitals=vitals_for_llm,
        risk=risk_result["risk"]
    )

    # Step 3: Update dashboard
    engine.update_vitals(
        heart_rate=data["heart_rate"],
        spo2=data["spo2"],
        temperature=data["temperature"],
        risk=risk_result["risk"],
        age=data["age"],
        gender=data["gender"],
        smoking=data["smoking"],
        hypertension=data["hypertension"],
        name=data.get("name", "John Doe")
    )

    # Step 4: Database logging
    patient_id = get_or_create_patient(data)
    log_vitals(patient_id, data, risk_result)

    # Step 5: Alert if high risk
    if risk_result["risk"] == "High":
        engine.process_event("abnormal_vitals")

        alert_message = f"""
⚠️ MEDICAL ALERT

Patient: {data.get("name", "Unknown")}
Status: HIGH RISK

Heart Rate: {data['heart_rate']} bpm
SpO2: {data['spo2']}%
Temperature: {data['temperature']}°C

Advice:
{advice}
"""
        whatsapp_agent.send_alert(alert_message)

    return jsonify({
        "risk": risk_result["risk"],
        "probability": risk_result["probability"],
        "advice": advice
    })

@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(engine.state)

@app.route("/charts")
def charts_page():
    return render_template("charts.html")



if __name__ == "__main__":
    app.run(debug=True)
