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

            # Activity from accelerometer
            "activity": "Unknown",

            # Environmental Data
            "humidity": "--",
            "room_temp": "--",
            "aqi": "--",

            # Intruder image
            "intruder_image": None,

            # Manual Emergency Status
            "manual_emergency": False
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

    def update_activity(self, activity):
        """Update patient activity status from accelerometer"""
        self.state["activity"] = activity
        return self.state

    def update_env_data(self, humidity, room_temp, aqi):
        """Update environmental metrics"""
        self.state["humidity"] = humidity
        self.state["room_temp"] = room_temp
        self.state["aqi"] = aqi
        return self.state

    def update_emergency(self, status):
        """Update manual emergency button status"""
        self.state["manual_emergency"] = bool(status)
        if status:
            self.state["alert"] = "MANUAL EMERGENCY"
        elif self.state["alert"] == "MANUAL EMERGENCY":
            self.state["alert"] = "None"
        return self.state




