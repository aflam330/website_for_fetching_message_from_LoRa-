/*
 * ESP32 LoRa Node
 * Connects ESP32 to LoRa module and communicates with Django LoRa Communication Dashboard
 * 
 * Hardware Connections:
 * ESP32    LoRa Module
 * GPIO 5   -> CS (NSS)
 * GPIO 23  -> MOSI
 * GPIO 19  -> MISO
 * GPIO 18  -> SCK
 * GPIO 2   -> RST
 * GPIO 4   -> DIO0
 * 3.3V     -> VCC
 * GND      -> GND
 */

#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============ CONFIGURATION - MODIFY THESE ============
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverURL = "http://192.168.1.100:8000";  // Your Django server IP
const char* esp32DeviceID = "ESP32-001";  // Must match registered node ID

// LoRa Pin Definitions
#define LORA_SCK     18
#define LORA_MISO    19
#define LORA_MOSI    23
#define LORA_CS      5
#define LORA_RST     2
#define LORA_DIO0    4

// LoRa Frequency (433E6 for Asia, 868E6 for Europe, 915E6 for North America)
#define LORA_FREQUENCY 433E6

// ============ SETUP ============
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("ESP32 LoRa Node Starting...");
  
  initWiFi();
  initLoRa();
  updateStatus("ONLINE");
  
  Serial.println("Setup complete!");
}

// ============ MAIN LOOP ============
void loop() {
  // Update status every 30 seconds
  static unsigned long lastStatusUpdate = 0;
  if (millis() - lastStatusUpdate > 30000) {
    updateStatus("ONLINE");
    lastStatusUpdate = millis();
  }
  
  // Check for incoming LoRa messages
  checkLoRaMessages();
  
  // Check inbox every 10 seconds
  static unsigned long lastInboxCheck = 0;
  if (millis() - lastInboxCheck > 10000) {
    checkInbox();
    lastInboxCheck = millis();
  }
  
  delay(100);
}

// ============ WiFi INITIALIZATION ============
void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  Serial.print("Connecting to WiFi");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

// ============ LoRa INITIALIZATION ============
void initLoRa() {
  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);
  
  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("LoRa initialization failed!");
    Serial.println("Check your wiring and antenna connection!");
    while (1);
  }
  
  // Configure LoRa parameters
  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(5);
  LoRa.setPreambleLength(8);
  LoRa.setSyncWord(0xF3);
  LoRa.enableCrc();
  
  Serial.println("LoRa initialized successfully!");
}

// ============ UPDATE STATUS TO SERVER ============
void updateStatus(const char* status) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
    return;
  }
  
  HTTPClient http;
  String url = String(serverURL) + "/communication/api/nodes/update-status/";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<200> doc;
  doc["esp32_device_id"] = esp32DeviceID;
  doc["status"] = status;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  int httpResponseCode = http.POST(jsonPayload);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("Status update: ");
    Serial.println(response);
  } else {
    Serial.print("Status update failed: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}

// ============ CHECK FOR LoRa MESSAGES ============
void checkLoRaMessages() {
  int packetSize = LoRa.parsePacket();
  
  if (packetSize) {
    uint8_t targetAddress = LoRa.read();
    uint8_t sourceAddress = LoRa.read();
    
    String message = "";
    while (LoRa.available()) {
      message += (char)LoRa.read();
    }
    
    Serial.print("LoRa RX from ");
    Serial.print(sourceAddress);
    Serial.print(": ");
    Serial.println(message);
    
    // Forward to Django server
    forwardLoRaMessageToServer(sourceAddress, message);
  }
}

// ============ FORWARD LoRa MESSAGE TO SERVER ============
void forwardLoRaMessageToServer(uint8_t sourceAddress, String message) {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  String url = String(serverURL) + "/communication/api/messages/send/";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<300> doc;
  doc["from_esp32_device_id"] = String("ESP32-") + String(sourceAddress, HEX);
  doc["to_esp32_device_id"] = esp32DeviceID;
  doc["payload"] = message;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  http.POST(jsonPayload);
  http.end();
}

// ============ CHECK INBOX FROM SERVER ============
void checkInbox() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  String url = String(serverURL) + "/communication/api/messages/inbox/" + String(esp32DeviceID) + "/";
  
  http.begin(url);
  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    
    StaticJsonDocument<2048> doc;
    deserializeJson(doc, response);
    
    if (doc["success"]) {
      JsonArray messages = doc["messages"];
      for (JsonObject msg : messages) {
        String content = msg["content"];
        String fromID = msg["from"]["esp32_device_id"];
        
        Serial.print("Message from ");
        Serial.print(fromID);
        Serial.print(": ");
        Serial.println(content);
      }
    }
  }
  
  http.end();
}

// ============ SEND MESSAGE VIA SERVER ============
void sendMessageToServer(String toESP32ID, String payload) {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  String url = String(serverURL) + "/communication/api/messages/send/";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<300> doc;
  doc["from_esp32_device_id"] = esp32DeviceID;
  doc["to_esp32_device_id"] = toESP32ID;
  doc["payload"] = payload;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  int httpResponseCode = http.POST(jsonPayload);
  
  if (httpResponseCode > 0) {
    Serial.println("Message sent successfully!");
  } else {
    Serial.println("Failed to send message!");
  }
  
  http.end();
}

// ============ SEND MESSAGE VIA LoRa ============
void sendLoRaMessage(String message, uint8_t targetAddress) {
  LoRa.beginPacket();
  LoRa.write(targetAddress);
  LoRa.write(0x01);  // Source address
  LoRa.print(message);
  LoRa.endPacket();
  
  Serial.print("LoRa TX to ");
  Serial.print(targetAddress);
  Serial.print(": ");
  Serial.println(message);
}

