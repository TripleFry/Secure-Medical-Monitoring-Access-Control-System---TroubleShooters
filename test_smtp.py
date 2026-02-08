import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

print(f"Testing SMTP with user: {SMTP_USER}")
print(f"Server: {SMTP_SERVER}:{SMTP_PORT}")

if not SMTP_USER or not SMTP_PASS:
    print("Error: SMTP_USER or SMTP_PASS not found in .env")
    exit(1)

try:
    msg = MIMEText("This is a test email from HealthGuard.")
    msg['Subject'] = "SMTP Test"
    msg['From'] = SMTP_USER
    msg['To'] = SMTP_USER # Send to self
    
    print("Connecting to server...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        print("Starting TLS...")
        server.starttls()
        print("Logging in...")
        server.login(SMTP_USER, SMTP_PASS)
        print("Sending message...")
        server.send_message(msg)
    print("✅ SMTP Test Successful! Email sent.")
except Exception as e:
    print(f"❌ SMTP Test Failed: {e}")
