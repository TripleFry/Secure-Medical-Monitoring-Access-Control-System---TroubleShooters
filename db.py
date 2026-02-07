import mysql.connector
import os

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Tanisop123@"),
        database=os.getenv("DB_NAME", "ieee")
    )

# Get or create patient
def get_or_create_patient(data):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if patient exists
    query = """
        SELECT id FROM patients
        WHERE name=%s AND age=%s AND gender=%s
    """
    cursor.execute(query, (data["name"], data["age"], data["gender"]))
    result = cursor.fetchone()

    if result:
        patient_id = result[0]
    else:
        insert_query = """
            INSERT INTO patients
            (name, age, gender, smoking, hypertension)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            data["name"],
            data["age"],
            data["gender"],
            data["smoking"],
            data["hypertension"]
        ))
        conn.commit()
        patient_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return patient_id


# Log only vitals
def log_vitals(patient_id, data, risk_result=None):
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure weight column exists
    try:
        cursor.execute("ALTER TABLE vitals_log ADD COLUMN weight DOUBLE AFTER temperature")
        conn.commit()
    except Exception:
        pass # Column already exists

    if risk_result is None:
        risk_result = {"risk": "Monitoring", "probability": 0.0}

    query = """
        INSERT INTO vitals_log
        (patient_id, heart_rate, spo2, temperature, weight, risk, probability)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        patient_id,
        data.get("heart_rate"),
        data.get("spo2"),
        data.get("temperature"),
        data.get("weight"),
        risk_result.get("risk", "Monitoring"),
        risk_result.get("probability", 0.0)
    ))

    conn.commit()
    cursor.close()
    conn.close()


# Log environmental data
def log_env_data(humidity, room_temp, aqi):
    conn = get_connection()
    cursor = conn.cursor()

    # First, ensure the table exists
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS environmental_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                humidity VARCHAR(10),
                room_temp VARCHAR(10),
                aqi VARCHAR(10),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except Exception:
        pass

    query = """
        INSERT INTO environmental_log (humidity, room_temp, aqi)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (str(humidity), str(room_temp), str(aqi)))
    
    conn.commit()
    cursor.close()
    conn.close()

# Fetch historical vitals for charts
def get_historical_vitals(patient_id, limit=50):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT heart_rate, spo2, temperature, weight, timestamp
        FROM vitals_log
        WHERE patient_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """

    cursor.execute(query, (patient_id, limit))
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results[::-1] # Return in chronological order

# Fetch historical environmental data for charts
def get_historical_env(limit=50):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT humidity, room_temp, aqi, timestamp
        FROM environmental_log
        ORDER BY timestamp DESC
        LIMIT %s
    """
    cursor.execute(query, (limit,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results[::-1] # Return in chronological order
