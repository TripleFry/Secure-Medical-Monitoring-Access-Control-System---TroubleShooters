from twilio.rest import Client

class WhatsAppAgent:
    def __init__(self, sid, token, from_number, to_number):
        self.client = Client(sid, token)
        self.from_number = from_number
        self.to_number = to_number

    def send_alert(self, message):
        print(f"📡 WhatsApp: Attempting to send alert from {self.from_number} to {self.to_number}...")
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )
            print(f"✅ WhatsApp: Message sent! SID: {msg.sid}")
            return True
        except Exception as e:
            print(f"❌ WhatsApp: Send Error: {e}")
            return False

