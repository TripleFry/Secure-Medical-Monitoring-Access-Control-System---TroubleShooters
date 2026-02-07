class EventEngine:
    def __init__(self):
        self.state = {
            "access_status": "No activity",
            "alert": "None"
        }

    def process_event(self, event_type, data=None):
        if event_type == "authorized":
            self.state["access_status"] = "Authorized access"
            self.state["alert"] = "None"
            print("[INFO] Authorized access granted")

        elif event_type == "intruder":
            self.state["access_status"] = "Intruder detected"
            self.state["alert"] = "SECURITY ALERT"
            print("[ALERT] Intruder detected!")

        elif event_type == "fall":
            self.state["alert"] = "MEDICAL EMERGENCY"
            print("[ALERT] Fall detected!")

        elif event_type == "abnormal_vitals":
            self.state["alert"] = "VITALS ALERT"
            print("[ALERT] Abnormal vitals!")

        else:
            print("[WARN] Unknown event")

        return self.state
