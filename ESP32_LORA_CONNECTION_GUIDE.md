# ESP32 + LoRa Module Connection Guide

This guide explains how to physically connect an ESP32 microcontroller with a LoRa module and integrate it with your Django LoRa Communication Dashboard.

## Table of Contents
1. [Hardware Connections](#hardware-connections)
2. [Required Components](#required-components)
3. [Wiring Diagram](#wiring-diagram)
4. [Software Setup](#software-setup)
5. [ESP32 Code Example](#esp32-code-example)
6. [Integration with Django Server](#integration-with-django-server)

---

## Hardware Connections

### Required Components

- **ESP32 Development Board** (ESP32-WROOM-32 or similar)
- **LoRa Module** (SX1278, SX1276, or compatible)
- **Breadboard** (optional, for prototyping)
- **Jumper wires**
- **Antenna** (for LoRa module - typically 433MHz or 868MHz/915MHz depending on your region)
- **Power supply** (USB cable for ESP32, 3.3V for LoRa module)

### Common LoRa Modules

1. **SX1278** (433MHz) - Most common, good range
2. **SX1276** (868MHz/915MHz) - Better for EU/US regions
3. **RA-02** (SX1278 based) - Popular breakout board
4. **Heltec LoRa32** - ESP32 + LoRa integrated board

---

## Wiring Diagram

### ESP32 to LoRa Module (SX1278/RA-02) Connections

| ESP32 Pin | LoRa Module Pin | Description |
|-----------|-----------------|-------------|
| GPIO 5    | NSS (CS)        | Chip Select (SPI) |
| GPIO 23   | MOSI            | Master Out Slave In (SPI) |
| GPIO 19   | MISO            | Master In Slave Out (SPI) |
| GPIO 18   | SCK             | Serial Clock (SPI) |
| GPIO 2    | RST             | Reset Pin |
| GPIO 4    | DIO0            | Digital I/O 0 (interrupt) |
| 3.3V      | VCC             | Power (3.3V) |
| GND       | GND             | Ground |

### Alternative Pin Configuration (if conflicts)

If the above pins conflict with your ESP32 board, you can use:

| ESP32 Pin | LoRa Module Pin | Description |
|-----------|-----------------|-------------|
| GPIO 15   | NSS (CS)        | Chip Select |
| GPIO 13   | MOSI            | SPI Data Out |
| GPIO 12   | MISO            | SPI Data In |
| GPIO 14   | SCK             | SPI Clock |
| GPIO 16   | RST             | Reset |
| GPIO 0    | DIO0            | Interrupt |

**Important Notes:**
- **Voltage**: LoRa modules typically run on 3.3V. Do NOT use 5V!
- **Antenna**: Always connect an antenna before powering on the LoRa module to prevent damage.
- **SPI**: ESP32 uses Hardware SPI (VSPI) by default on pins 23, 19, 18, 5.

---

## Software Setup

### 1. Install Arduino IDE or PlatformIO

**Option A: Arduino IDE**
1. Download from: https://www.arduino.cc/en/software
2. Install ESP32 Board Support:
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "ESP32" → Install

**Option B: PlatformIO** (Recommended)
- Install VS Code extension: PlatformIO IDE
- More modern and easier dependency management

### 2. Install Required Libraries

For Arduino IDE:
- Go to Sketch → Include Library → Manage Libraries
- Install:
  - **LoRa** by Sandeep Mistry (version 0.8.0 or later)
  - **WiFi** (built-in with ESP32)
  - **HTTPClient** (built-in with ESP32)
  - **ArduinoJson** (for JSON parsing)

For PlatformIO:
Add to `platformio.ini`:
```ini
lib_deps = 
    sandeepmistry/LoRa@^0.8.0
    bblanchon/ArduinoJson@^6.21.0
```

---

## ESP32 Code Example

Here's a complete example that connects ESP32 to LoRa module and communicates with your Django server:

```cpp
#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============ CONFIGURATION ============
// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Django Server Configuration
const char* serverURL = "http://192.168.1.100:8000";  // Change to your Django server IP
const char* esp32DeviceID = "ESP32-001";  // Must match your registered node ID

// LoRa Configuration
#define LORA_SCK     18    // GPIO18 - SCK
#define LORA_MISO    19    // GPIO19 - MISO
#define LORA_MOSI    23    // GPIO23 - MOSI
#define LORA_CS      5     // GPIO5 - CS
#define LORA_RST     2     // GPIO2 - RST
#define LORA_DIO0    4     // GPIO4 - DIO0

// LoRa Frequency (change based on your region)
// 433E6 for Asia, 868E6 for Europe, 915E6 for North America
#define LORA_FREQUENCY 433E6

// ============ SETUP ============
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("ESP32 LoRa Node Starting...");
  
  // Initialize WiFi
  initWiFi();
  
  // Initialize LoRa
  initLoRa();
  
  // Register with Django server
  registerWithServer();
  
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
  
  // Check for messages from Django server
  checkInbox();
  
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
  // Configure LoRa pins
  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);
  
  // Initialize LoRa at specified frequency
  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("LoRa initialization failed!");
    while (1); // Halt if LoRa fails
  }
  
  // Configure LoRa parameters
  LoRa.setSpreadingFactor(7);      // Range: 6-12, higher = longer range but slower
  LoRa.setSignalBandwidth(125E3);  // Bandwidth: 7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3, 250E3, 500E3
  LoRa.setCodingRate4(5);          // Coding rate: 5-8, higher = better error correction
  LoRa.setPreambleLength(8);       // Preamble length
  LoRa.setSyncWord(0xF3);          // Sync word (0x12 for public, 0x34 for private)
  LoRa.enableCrc();                // Enable CRC
  
  Serial.println("LoRa initialized successfully!");
}

// ============ REGISTER WITH SERVER ============
void registerWithServer() {
  updateStatus("ONLINE");
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
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["esp32_device_id"] = esp32DeviceID;
  doc["status"] = status;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  int httpResponseCode = http.POST(jsonPayload);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("Status update response: ");
    Serial.println(response);
  } else {
    Serial.print("Status update failed: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}

// ============ SEND MESSAGE VIA LoRa ============
void sendLoRaMessage(String message, uint8_t targetAddress) {
  LoRa.beginPacket();
  LoRa.write(targetAddress);  // Target address
  LoRa.write(0x01);           // Source address (you can set this)
  LoRa.print(message);
  LoRa.endPacket();
  
  Serial.print("LoRa message sent: ");
  Serial.println(message);
}

// ============ CHECK FOR LoRa MESSAGES ============
void checkLoRaMessages() {
  int packetSize = LoRa.parsePacket();
  
  if (packetSize) {
    // Read packet header
    uint8_t targetAddress = LoRa.read();
    uint8_t sourceAddress = LoRa.read();
    
    // Read payload
    String message = "";
    while (LoRa.available()) {
      message += (char)LoRa.read();
    }
    
    // Print received message
    Serial.print("LoRa message received from ");
    Serial.print(sourceAddress);
    Serial.print(": ");
    Serial.println(message);
    
    // Optionally forward to Django server
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
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck < 10000) return; // Check every 10 seconds
  lastCheck = millis();
  
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  String url = String(serverURL) + "/communication/api/messages/inbox/" + String(esp32DeviceID) + "/";
  
  http.begin(url);
  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    
    // Parse JSON response
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
        
        // Optionally send via LoRa to another node
        // sendLoRaMessage(content, targetAddress);
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
```

---

## Integration with Django Server

### Architecture Overview

```
┌─────────────┐         WiFi/HTTP          ┌──────────────┐
│   ESP32     │◄──────────────────────────►│   Django     │
│  + LoRa     │                             │   Server     │
└──────┬──────┘                             └──────────────┘
       │
       │ LoRa Radio
       │
┌──────▼──────┐
│ Other LoRa  │
│   Nodes     │
└─────────────┘
```

### Connection Flow

1. **ESP32 connects to WiFi** → Gets IP address
2. **ESP32 initializes LoRa module** → Ready for LoRa communication
3. **ESP32 registers with Django** → Sends status update to `/communication/api/nodes/update-status/`
4. **ESP32 can now:**
   - Send messages via HTTP to Django server
   - Receive messages from Django server via HTTP
   - Send/receive messages via LoRa radio
   - Forward LoRa messages to Django server

### API Endpoints Used

1. **Update Status**: `POST /communication/api/nodes/update-status/`
   ```json
   {
     "esp32_device_id": "ESP32-001",
     "status": "ONLINE"
   }
   ```

2. **Send Message**: `POST /communication/api/messages/send/`
   ```json
   {
     "from_esp32_device_id": "ESP32-001",
     "to_esp32_device_id": "ESP32-002",
     "payload": "Hello!"
   }
   ```

3. **Get Inbox**: `GET /communication/api/messages/inbox/ESP32-001/`

---

## Troubleshooting

### LoRa Module Not Working

1. **Check wiring** - Ensure all SPI pins are connected correctly
2. **Check voltage** - LoRa module must be 3.3V, not 5V!
3. **Check antenna** - Antenna must be connected before powering on
4. **Check frequency** - Ensure frequency matches your region:
   - 433MHz for Asia
   - 868MHz for Europe
   - 915MHz for North America
5. **Check SPI pins** - Verify pins match your ESP32 board

### WiFi Connection Issues

1. **Check credentials** - Verify SSID and password
2. **Check signal strength** - ESP32 may be too far from router
3. **Check IP address** - Ensure Django server IP is correct
4. **Check firewall** - Ensure Django server allows connections

### Django Server Not Responding

1. **Check server is running** - `python manage.py runserver`
2. **Check IP address** - Use `0.0.0.0:8000` to allow external connections:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
3. **Check node registration** - Ensure ESP32 device ID is registered in Django
4. **Check CORS** - Django endpoints are CSRF-exempt, so should work fine

---

## Next Steps

1. **Upload code to ESP32** with your WiFi credentials and Django server IP
2. **Register your node** in Django via the web interface or admin panel
3. **Test connection** by checking if status updates appear in Django dashboard
4. **Test messaging** by sending messages between nodes
5. **Deploy** multiple nodes to create a LoRa mesh network

---

## Additional Resources

- **LoRa Library Documentation**: https://github.com/sandeepmistry/arduino-LoRa
- **ESP32 Arduino Core**: https://github.com/espressif/arduino-esp32
- **LoRaWAN vs LoRa**: This guide uses raw LoRa. For LoRaWAN, consider using LoRaWAN libraries.

---

## Notes

- **Range**: LoRa can reach 2-15 km in open areas, less in urban environments
- **Power**: LoRa is low-power, suitable for battery-operated devices
- **Data Rate**: LoRa is slow (0.3-50 kbps) but reliable over long distances
- **Security**: Consider adding encryption for production use

