#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// Replace with your server URL, include port if not 80, e.g. "http://192.168.1.50:5000/esp32" 
const char* serverUrl = "http://YOUR_SERVER_IP:5000/esp32";

void setup() {
  Serial.begin(115200);
  delay(100);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Example sensor values - replace with real sensor reads
    int heart_rate = 72;
    float spo2 = 98.5;
    float temperature = 36.6;
    int age = 45;

    String payload = "{";
    payload += "\"device_id\": \"esp32-01\",";
    payload += "\"name\": \"Alice\",";
    payload += "\"age\": "; payload += age; payload += ",";
    payload += "\"heart_rate\": "; payload += heart_rate; payload += ",";
    payload += "\"spo2\": "; payload += String(spo2); payload += ",";
    payload += "\"temperature\": "; payload += String(temperature);
    payload += "}";

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("Response code: ");
      Serial.println(httpResponseCode);
      Serial.print("Response: ");
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }

  // Post every 10 seconds (adjust as needed)
  delay(10000);
}
