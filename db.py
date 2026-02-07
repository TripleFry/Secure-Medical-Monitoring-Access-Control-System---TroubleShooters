import mysql.connector
import os

def get_connection():
    return mysql.connector.connect(
       host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
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
def log_vitals(patient_id, data, risk_result):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO vitals_log
        (patient_id, heart_rate, spo2, temperature, risk, probability)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        patient_id,
        data["heart_rate"],
        data["spo2"],
        data["temperature"],
        risk_result["risk"],
        risk_result["probability"]
    ))

    conn.commit()
    cursor.close()
    conn.close()
