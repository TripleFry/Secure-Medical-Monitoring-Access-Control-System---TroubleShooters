import numpy as np
import pandas as pd

np.random.seed(42)

n_samples = 200000
data = []

for _ in range(n_samples):

    age = np.random.randint(18, 90)
    gender = np.random.choice(['Male', 'Female'])
    weight = np.random.uniform(50, 100)
    height = np.random.uniform(1.5, 1.9)

    smoking = np.random.choice([0, 1], p=[0.75, 0.25])
    hypertension = np.random.choice([0, 1], p=[0.8, 0.2])

    # Slightly clearer vitals separation
    base_hr = np.random.normal(80, 12)
    base_temp = np.random.normal(37.0, 0.5)
    base_spo2 = np.random.normal(96, 2)

    # Clip to medical ranges
    hr = np.clip(base_hr, 50, 140)
    temp = np.clip(base_temp, 35.5, 40)
    spo2 = np.clip(base_spo2, 85, 100)

    # ---- Risk scoring ----
    risk_score = 0

    # heart rate
    if hr > 105:
        risk_score += 3
    elif hr > 95:
        risk_score += 2
    elif hr > 85:
        risk_score += 1

    # temperature
    if temp > 38:
        risk_score += 2
    elif temp > 37.5:
        risk_score += 1

    # oxygen
    if spo2 < 90:
        risk_score += 3
    elif spo2 < 94:
        risk_score += 2

    # age
    if age > 65:
        risk_score += 1

    # conditions
    if smoking:
        risk_score += 1
    if hypertension:
        risk_score += 2

    # Convert score to probability (less noise)
    prob = 1 / (1 + np.exp(-1.2 * (risk_score - 3)))

    risk = np.random.choice([0, 1], p=[1 - prob, prob])

    data.append([
        hr, temp, spo2,
        age, gender, weight, height,
        smoking, hypertension,
        risk
    ])

columns = [
    'Heart Rate',
    'Body Temperature',
    'Oxygen Saturation',
    'Age',
    'Gender',
    'Weight (kg)',
    'Height (m)',
    'Smoking',
    'Hypertension',
    'Risk Category'
]

df = pd.DataFrame(data, columns=columns)

df['Risk Category'] = df['Risk Category'].map({
    0: 'Normal',
    1: 'High Risk'
})

df.to_csv("realistic_patient_data.csv", index=False)
print("Semi-realistic dataset created!")
