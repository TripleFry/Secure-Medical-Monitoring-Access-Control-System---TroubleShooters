from twilio.rest import Client
import time

class WhatsAppAgent:
    def __init__(self, sid, token, from_number, to_number):
        self.client = Client(sid, token)
        self.from_number = from_number
        self.to_number = to_number
        self.last_sent_time = 0

    def send_alert(self, message):
        # Enforce 30-second cooldown
        current_time = time.time()
        if current_time - self.last_sent_time < 30:
            print(f"⏳ WhatsApp: Cooldown active. Skipping alert to prevent spam.")
            return False

        print(f"📡 WhatsApp: Attempting to send alert from {self.from_number} to {self.to_number}...")
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )
            print(f"✅ WhatsApp: Message sent! SID: {msg.sid}")
            self.last_sent_time = current_time
            return True
        except Exception as e:
            print(f"❌ WhatsApp: Send Error: {e}")
            return False

