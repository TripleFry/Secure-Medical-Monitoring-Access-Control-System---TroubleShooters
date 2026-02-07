from groq import Groq

class ClinicalAgent:
    def __init__(self, api_key, model="openai/gpt-oss-120b"):
        self.client = Groq(api_key=api_key)
        self.model = model

    def generate_advice(self, vitals, risk):
        prompt = f"""
You are a medical monitoring assistant.

Patient data:
- Age: {vitals['age']}
- Heart Rate: {vitals['heart_rate']} bpm
- SpO2: {vitals['spo2']}%
- Temperature: {vitals['temperature']} °C
- ML Risk Prediction: {risk}

Your task:
1. Briefly explain the patient's condition.
2. Provide 3–5 safe, practical care recommendations.
3. Keep the response short and clear.
4. Do NOT give drug prescriptions.
5. The message should be well formatted for Whatsapp display,using emojis and line breaks for clarity.

"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a clinical decision assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content
