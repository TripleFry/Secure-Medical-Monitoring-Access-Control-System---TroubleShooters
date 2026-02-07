import joblib

class HealthAgent:
    def __init__(self, model_path="model.pkl", scaler_path="scaler.pkl"):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def preprocess(self, data):
        # Encode gender exactly like training
        gender = 0 if data["gender"].lower() == "male" else 1

        # Smoking & hypertension already numeric (0 or 1)
        smoking = int(data["smoking"])
        hypertension = int(data["hypertension"])

        # Calculate BMI
        weight = data["weight"]
        height = data["height"]
        bmi = weight / (height ** 2)

        # Derived binary features
        fever = 1 if data["temperature"] > 37.5 else 0
        low_spo2 = 1 if data["spo2"] < 94 else 0

        features = [
            data["heart_rate"],     # 1
            data["temperature"],    # 2
            data["spo2"],           # 3
            data["age"],            # 4
            gender,                 # 5
            weight,                 # 6
            height,                 # 7
            smoking,                # 8
            hypertension,           # 9
            bmi,                    # 10
            fever,                  # 11
            low_spo2                # 12
        ]

        return features

    def predict(self, data):
        features = self.preprocess(data)

        # Scale
        scaled = self.scaler.transform([features])

        # Predict
        pred = self.model.predict(scaled)[0]
        prob = self.model.predict_proba(scaled)[0][1]

        risk_label = "High" if pred == 1 else "Normal"

        return {
            "risk": risk_label,
            "probability": float(prob)
        }
