from twilio.rest import Client

class WhatsAppAgent:
    def __init__(self, sid, token, from_number, to_number):
        self.client = Client(sid, token)
        self.from_number = from_number
        self.to_number = to_number

    def send_alert(self, message):
        self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=self.to_number
        )
