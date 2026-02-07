class EventEngine:
    def __init__(self):
        self.state = {
            "access_status": "No activity",
            "alert": "None",

            # Vitals
            "heart_rate": "--",
            "spo2": "--",
            "temperature": "--",
            "risk": "--",

            # Profile
            "name": "John Doe",
            "age": "--",
            "gender": "--",
            "smoking": "--",
            "hypertension": "--",

            # Intruder image
            "intruder_image": None
        }

    def process_event(self, event_type, image_path=None):

        if event_type == "authorized":
            self.state["access_status"] = "Authorized access"
            self.state["alert"] = "None"

        elif event_type == "intruder_detected":
            self.state["access_status"] = "Intruder detected"
            self.state["alert"] = "SECURITY ALERT"
            self.state["intruder_image"] = image_path

        elif event_type == "abnormal_vitals":
            self.state["alert"] = "MEDICAL EMERGENCY"

        return self.state

    def update_vitals(self, heart_rate, spo2, temperature, risk,
                      age, gender, smoking, hypertension, name="John Doe"):

        self.state["heart_rate"] = heart_rate
        self.state["spo2"] = spo2
        self.state["temperature"] = temperature
        self.state["risk"] = risk

        self.state["name"] = name
        self.state["age"] = age
        self.state["gender"] = gender
        self.state["smoking"] = smoking
        self.state["hypertension"] = hypertension
