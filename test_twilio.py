import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

sid = os.getenv("TWILIO_ACCOUNT_SID")
token = os.getenv("TWILIO_AUTH_TOKEN")
from_num = os.getenv("TWILIO_WHATSAPP_NUMBER")
to_num = os.getenv("DOCTOR_WHATSAPP_NUMBER")

print(f"DEBUG: SID={sid}")
print(f"DEBUG: FROM={from_num}")
print(f"DEBUG: TO={to_num}")

if not all([sid, token, from_num, to_num]):
    print("❌ Error: Missing Twilio credentials in .env")
    exit(1)

client = Client(sid, token)

try:
    print("🚀 Attempting to send TEST message...")
    message = client.messages.create(
        body="HealthGuard WhatsApp Test: This confirms your Twilio connection is working!",
        from_=from_num,
        to=to_num
    )
    print(f"✅ Success! SID: {message.sid}")
    print(f"Status: {message.status}")
except Exception as e:
    print(f"❌ Twilio Error: {e}")
    if "Sandbox" in str(e) or "Opt-in" in str(e):
        print("\n💡 TIP: If you're using Twilio Sandbox, you MUST send a message from your phone TO the Twilio number first (e.g., 'join [sandbox-word]').")
