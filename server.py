from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_cors import CORS
from event_engine import EventEngine
from health_agent import HealthAgent
from clinical_agent import ClinicalAgent
from whatsapp_agent import WhatsAppAgent
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from dotenv import load_dotenv
from db import get_or_create_patient, log_vitals
from db import get_connection
from datetime import datetime
from sqlalchemy import text

# Import auth functions
try:
    from auth import (
        create_users_table, create_user, authenticate_user, 
        get_user_by_email, verify_user_token
    )
    AUTH_ENABLED = True
    # Try to create users table
    try:
        create_users_table()
        print("✓ Users table initialized")
    except Exception as e:
        print(f"Warning: Could not create users table: {e}")
        print("Authentication will use session-only mode")
        AUTH_ENABLED = False
except ImportError as e:
    print(f"Warning: Auth module not available: {e}")
    AUTH_ENABLED = False


load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Enable CORS for all routes (optional token validation for sensitive endpoints)
CORS(app, resources={r"/*": {"origins": "*"}})

# Optional: Load API token from env for /esp32 and /activity endpoints
API_TOKEN = os.getenv("SENSOR_API_TOKEN", None)

@app.before_request
def log_request_info():
    print(f"[REQUEST] {request.method} {request.path} from {request.remote_addr}")


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

# SMTP Configuration (Placeholder)
SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

def send_verification_email(email, token):
    """Send a verification email to the user (Placeholder/Console logger)"""
    verification_link = f"http://{request.host}/verify?email={email}&token={token}"
    
    # In a real app, you would use smtplib here. 
    # For now, we'll log it to the console so the user can verify.
    print("\n" + "="*50)
    print("📧 VERIFICATION EMAIL SENT 📧")
    print(f"To: {email}")
    print(f"Link: {verification_link}")
    print("="*50 + "\n")
    
    # Optional logic for real email sending if configured
    if SMTP_USER and SMTP_PASS:
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(f"Please click the link below to verify your email:\n{verification_link}")
            msg['Subject'] = "Verify your HealthGuard Account"
            msg['From'] = SMTP_USER
            msg['To'] = email
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            print("✅ Real email sent successfully!")
        except Exception as e:
            print(f"❌ Failed to send real email: {e}")

# Authentication routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email or not password:
            return render_template("login.html", error="Email and password are required")
        
        if AUTH_ENABLED:
            # Use database authentication with bcrypt
            result = authenticate_user(email, password)
            if result["success"]:
                session["logged_in"] = True
                session["user_id"] = result["user"]["id"]
                session["user_email"] = result["user"]["email"]
                session["user_name"] = result["user"]["full_name"]
                session["user_role"] = result["user"]["role"]
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error=result.get("error", "Login failed"))
        else:
            # Fallback: session-only mode (demo)
            session["logged_in"] = True
            session["user_email"] = email
            return redirect(url_for("dashboard"))
            
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        role = request.form.get("role")
        
        if not all([email, password, fullname, role]):
            return render_template("signup.html", error="All fields are required")
        
        if AUTH_ENABLED:
            # Use database with bcrypt
            result = create_user(email, password, fullname, role)
            if result["success"]:
                # Send verification email
                send_verification_email(email, result["verification_token"])
                
                # Show success message instead of auto-login
                return render_template("signup.html", 
                    success="Account created! Please check your email and click the verification link to proceed.")
            else:
                error_msg = result.get("error", "Signup failed")
                if "Duplicate entry" in error_msg:
                    error_msg = "This email is already registered"
                return render_template("signup.html", error=error_msg)
        else:
            # Fallback: session-only mode (demo)
            session["logged_in"] = True
            session["user_email"] = email
            session["user_name"] = fullname
            session["user_role"] = role
            return redirect(url_for("dashboard"))
            
    return render_template("signup.html")

@app.route("/verify")
def verify():
    email = request.args.get("email")
    token = request.args.get("token")
    
    if not email or not token:
        return render_template("verify.html", error="Invalid verification link")
    
    if verify_user_token(email, token):
        return render_template("verify.html", success=True)
    else:
        return render_template("verify.html", error="Invalid or expired token")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/alerts")
def alerts_page():
    return render_template("alerts.html")

@app.route("/report")
def download_report():
    state = engine.state
    
    report_content = f"""
=========================================
      HEALTHGUARD MEDICAL REPORT
=========================================
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PATIENT INFORMATION
-------------------
Name:         {state.get('name', 'N/A')}
Age:          {state.get('age', 'N/A')}
Gender:       {state.get('gender', 'N/A')}
Smoking:      {state.get('smoking', 'N/A')}
Hypertension: {state.get('hypertension', 'N/A')}

LATEST VITALS
-------------
Heart Rate:   {state.get('heart_rate', '--')} BPM
SpO2:         {state.get('spo2', '--')}%
Temperature:  {state.get('temperature', '--')}°C
Health Risk:  {state.get('risk', '--')}

ENVIRONMENT
-----------
Room Temp:    {state.get('room_temp', '--')}°C
Humidity:     {state.get('humidity', '--')}%
AQI:          {state.get('aqi', '--')}

ACTIVITY & STATUS
-----------------
Current Activity: {state.get('activity', 'Unknown')}
Alert Status:     {state.get('alert', 'None')}

-----------------------------------------
This is an automated report generated by
HealthGuard Medical Monitoring System.
=========================================
"""
    from flask import Response
    return Response(
        report_content,
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename=Patient_Report_Ramesh_Gupta.txt"}
    )




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


@app.route("/activity", methods=["POST"])
def receive_activity():
    """Endpoint to receive posture/activity data from detector or ESP32"""
    data = request.json
    activity = data.get("activity", "Unknown")
    device_id = data.get("device_id", "unknown")
    
    # Validate activity value
    valid_activities = ["Sitting", "Standing", "Sleeping", "Unknown"]
    if activity not in valid_activities:
        return jsonify({"error": "Invalid activity value"}), 400
    
    print(f"[ACTIVITY] Update: {activity} from {device_id}")
    
    # Update state
    state = engine.update_activity(activity)
    
    return jsonify({"status": "success", "activity": activity})


@app.route("/env", methods=["POST"])
def receive_env():
    """Endpoint to receive environmental sensor data"""
    data = request.json
    humidity = data.get("humidity", "--")
    room_temp = data.get("room_temp", "--")
    aqi = data.get("aqi", "--")
    
    # Update state
    state = engine.update_env_data(humidity, room_temp, aqi)
    
    # DB logging
    try:
        from db import log_env_data
        log_env_data(humidity, room_temp, aqi)
    except Exception as e:
        print(f"Env Log Error: {e}")

    return jsonify({"status": "success", "data": state})




@app.route("/esp32", methods=["POST"])
def esp32_post():
    """Endpoint for ESP32 devices to POST sensor JSON."""
    try:
        raw_data = request.json or {}
        
        # Sanitize keys: Robust case-insensitive parsing
        data = {}
        for k, v in raw_data.items():
            data[str(k).lower().strip()] = v
            
        print(f"[ESP32] Received Data: {data}")


        # Vital key mapping
        # Vital key mapping with non-zero prioritization
        def get_best_vital(keys):
            best_val = None
            for k in keys:
                val = data.get(k)
                if val is not None:
                    # Prefer non-zero values (handles both int and string '0')
                    is_zero = (str(val).strip() == "0" or val == 0)
                    is_best_zero = (best_val is None or str(best_val).strip() == "0" or best_val == 0)
                    
                    if best_val is None or (is_best_zero and not is_zero):
                        best_val = val
            return best_val

        heart_rate = get_best_vital(["heart_rate", "hr", "pulse", "bpm"])
        spo2 = get_best_vital(["spo2", "spo", "ox", "oxygen"])
        temperature = get_best_vital(["temperature", "temp", "t"])

        print(f"DEBUG: Mapped Vitals -> HR: {heart_rate}, SpO2: {spo2}, Temp: {temperature}")

        # Demographic data (Strictly Hardcoded)
        name = "Ramesh Gupta"
        age = 20
        gender = "male"
        smoking = False
        hypertension = False
        weight = 70.0  # Strictly Hardcoded
        
        # Parameters remaining in payload
        height = data.get("height")





        # Environmental data
        humidity = data.get("humidity")
        room_temp = data.get("room_temp")
        aqi = data.get("aqi")
        emergency = data.get("emergency")  # Manual button status
        fall = data.get("fall")  # Fall detection status
        posture = data.get("posture")  # Activity/Posture status

        timestamp = datetime.utcnow().isoformat()

        # Update activity if provided
        if posture:
            engine.update_activity(posture)


        # Always update environmental data if provided
        if humidity is not None or room_temp is not None or aqi is not None:
            engine.update_env_data(
                humidity=humidity or "--",
                room_temp=room_temp or "--",
                aqi=aqi or "--"
            )
            # Log to DB
            try:
                from db import log_env_data
                log_env_data(humidity or "--", room_temp or "--", aqi or "--")
            except Exception as e:
                print(f"❌ ESP32 Env DB Log Error: {e}")

        # Update manual emergency status
        if emergency is not None:
            engine.update_emergency(emergency)
            if emergency:
                print("🚨 MANUAL EMERGENCY BUTTON PRESSED!")
                emergency_alert = f"🆘 EMERGENCY: Help button pressed by {name}! Please respond immediately."
                whatsapp_agent.send_alert(emergency_alert)

        # Update fall status and alert
        if fall is not None:
            engine.update_fall(fall)
            if fall:
                print("🚨 FALL DETECTED! Sending alert...")
                fall_alert = f"⚠️ EMERGENCY: Fall detected for {name}! Please check the patient immediately."
                whatsapp_agent.send_alert(fall_alert)

        # Update Engine for immediate dashboard feedback (Partial or Full)
        if heart_rate is not None or spo2 is not None or temperature is not None:
            engine.update_vitals(
                heart_rate=heart_rate,
                spo2=spo2,
                temperature=temperature,
                name=name,
                age=age,
                gender=gender,
                smoking=smoking,
                hypertension=hypertension
            )

        # Database logging for ALL vitals (Partial or Full)
        if heart_rate is not None or spo2 is not None or temperature is not None:
            try:
                # Use a payload dict for patient lookup
                lookup_payload = {
                    "name": name,
                    "age": age or 0,
                    "gender": gender,
                    "smoking": smoking,
                    "hypertension": hypertension
                }
                patient_id = get_or_create_patient(lookup_payload)
                
                # Log current vitals state
                vitals_payload = {
                    "heart_rate": heart_rate,
                    "spo2": spo2,
                    "temperature": temperature,
                    "weight": weight
                }
                
                log_vitals(patient_id, vitals_payload)
                print(f"✅ Vitals logged to DB for Patient {patient_id}")
            except Exception as db_e:
                print(f"❌ DB Log Error: {db_e}")
                # Secondary persistence
                with open("esp32_vitals.csv", "a") as f:
                    f.write(f"{timestamp},{device_id},{name},{age},{gender},{heart_rate},{spo2},{temperature}\n")

        # Full Health Flow Path (AI Analysis)
        if heart_rate is not None and spo2 is not None and temperature is not None and age is not None:
            print("🚀 Triggering AI Health Flow...")
            payload = {
                "age": int(age),
                "heart_rate": int(heart_rate),
                "spo2": float(spo2),
                "temperature": float(temperature),
                "gender": gender,
                "smoking": bool(smoking),
                "hypertension": bool(hypertension),
                "weight": float(weight) if weight is not None else 70.0,
                "height": float(height) if height is not None else 1.75,
                "name": name
            }

            # Health prediction
            risk_result = health_agent.predict(payload)
            print(f"🧠 Risk Result: {risk_result}")

            advice = clinical_agent.generate_advice(
                vitals={k: payload[k] for k in ["age", "heart_rate", "spo2", "temperature"]},
                risk=risk_result["risk"]
            )

            engine.update_vitals(
                heart_rate=payload["heart_rate"],
                spo2=payload["spo2"],
                temperature=payload["temperature"],
                risk=risk_result["risk"],
                age=payload["age"],
                gender=payload["gender"],
                smoking=payload["smoking"],
                hypertension=payload["hypertension"],
                name=payload.get("name", "ESP32")
            )

            if risk_result.get("risk") == "High":
                engine.process_event("abnormal_vitals")
                
                # WhatsApp Alert
                try:
                    # Truncate advice to fit Twilio's limit
                    max_advice_length = 800
                    truncated_advice = advice[:max_advice_length]
                    if len(advice) > max_advice_length:
                        truncated_advice += "..."

                    alert_message = f"""⚠️ MEDICAL ALERT (ESP32)

Patient: {name}
Status: HIGH RISK (AI Analysis)

Vitals:
• Heart Rate: {payload['heart_rate']} bpm
• SpO2: {payload['spo2']}%
• Temperature: {payload['temperature']}°C

Advice:
{truncated_advice}

Please check the dashboard for live updates."""
                    whatsapp_agent.send_alert(alert_message)
                    print(f"📲 WhatsApp Alert Sent to Doctor for {name}")
                except Exception as wa_e:
                    print(f"❌ WhatsApp Alert Failed: {wa_e}")

            return jsonify({"status": "ok", "risk": risk_result.get("risk"), "advice": advice})


        # Dashboard Update Path (Live view)
        if heart_rate or spo2 or temperature:
            print("📈 Updating Live Dashboard...")
            engine.update_vitals(
                heart_rate=heart_rate,
                spo2=spo2,
                temperature=temperature,
                risk="Monitoring",
                age=age or "--",
                gender=gender,
                smoking=smoking,
                hypertension=hypertension,
                name=name
            )

        # Log to consolidated CSV
        with open("esp32_sensor_log.csv", "a") as f:
            f.write(f"{timestamp},{device_id},{name},{heart_rate},{spo2},{temperature},{humidity},{room_temp},{aqi}\n")

        print("✨ Sensor data update complete")
        return jsonify({"status": "ok", "message": "Sensor data updated"})


    except Exception as e:
        print(f"💥 ESP32 Endpoint Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500









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

        # Truncate advice to fit Twilio's 1600 character limit
        max_advice_length = 800
        truncated_advice = advice[:max_advice_length]
        if len(advice) > max_advice_length:
            truncated_advice += "..."

        alert_message = f"""⚠️ MEDICAL ALERT

Patient: {data.get("name", "Unknown")}
Status: HIGH RISK

Vitals:
• Heart Rate: {data['heart_rate']} bpm
• SpO2: {data['spo2']}%
• Temperature: {data['temperature']}°C
• Age: {data.get('age', 'N/A')}

Advice:
{truncated_advice}

Please check the dashboard for full details.
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



@app.route("/api/history/vitals")
def vitals_history():
    try:
        from db import get_historical_vitals
        # For single patient, always use patient_id 6 (Ramesh Gupta)
        # or we could fetch the first patient ID from DB dynamically
        data = get_historical_vitals(6) 
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/history/env")
def env_history():
    try:
        from db import get_historical_env
        data = get_historical_env()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

