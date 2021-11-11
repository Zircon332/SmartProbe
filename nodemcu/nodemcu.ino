#include <Arduino.h>
#include <DallasTemperature.h>
#include <Preferences.h>
#include <OneWire.h>
#include <SPI.h>
#include <stdio.h>
#include <stdlib.h>
#include <WiFi.h>

#include "esp32-hal-ledc.h"
#include "BMP.h"
#include "Config.h"
#include "OV7670.h"

#define WIFI_TIMEOUT_MS 20000

#define SPRAYER_PIN 18
#define SPRINKLER_PIN 5

#define MOISTURE_PIN 39
#define TEMPERATURE_PIN 23

#define TIMER_WIDTH 16

// Camera pins
// ---===---
#define SIOD 21
#define SIOC 22

#define VSYNC 34
#define HREF 35

#define XCLK 32
#define PCLK 33

#define D0 27
#define D1 17
#define D2 16
#define D3 15
#define D4 14
#define D5 13
#define D6 12
#define D7 4
// ---===---

IPAddress server(address[0], address[1], address[2], address[3]);
WiFiClient client;

OneWire oneWire(TEMPERATURE_PIN);
DallasTemperature sensorTemperature(&oneWire);
OV7670* camera;

Preferences preferences;

const char* DELIMITER = "!#)%@#^#$]";
unsigned char bmpHeader[BMP::headerSize];
String id;

unsigned long last = 0;

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long startAttemptTime = millis();

  while(WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < WIFI_TIMEOUT_MS) {
    Serial.print(".");
    delay(100);
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println(" Failed!");
  } else {
    Serial.println(" Connected!");
  }
}

void connectToServer() {
  if (client.connect(server, 12345)) {
    Serial.println("Connected to server.");
  } else {
    Serial.println("Failed to connect to server.");
  }
}

void setup() {
  Serial.begin(9600);
  
  pinMode(MOISTURE_PIN, INPUT);
  pinMode(SPRAYER_PIN, OUTPUT);
  pinMode(SPRINKLER_PIN,OUTPUT);
  
  sensorTemperature.begin();
  sensorTemperature.setResolution(12);
  
  camera = new OV7670(OV7670::Mode::QQVGA_RGB565, SIOD, SIOC, VSYNC, HREF, XCLK, PCLK, D0, D1, D2, D3, D4, D5, D6, D7);
  BMP::construct16BitHeader(bmpHeader, camera->xres, camera->yres);
  
  ledcSetup(4,50,TIMER_WIDTH);
  ledcAttachPin(SPRAYER_PIN,4);

  // Uncomment the following block if you want to clear the non-volatile memory
//  preferences.begin("probe", false);
//  preferences.clear();
//  preferences.end();

  // Read ID from non-volatile memory
  preferences.begin("probe", true); // true = Read-only mode
  id = preferences.getString("id", "None"); // Default to "None" string
  preferences.end();
}

void loop() {
  // Read sensor values
  int moisture = analogRead(MOISTURE_PIN);
  sensorTemperature.requestTemperatures();
  float temperature = sensorTemperature.getTempCByIndex(0);
  
  camera->oneFrame();
  
  if (WiFi.status() == WL_CONNECTED && client.connected()) {   
    // Only send data every 10 seconds
    if (millis() - last > 10000) {
      Serial.print("ID: ");
      Serial.println(id);
      
      Serial.print("Moisture: ");
      Serial.println(moisture);
    
      Serial.print("Temperature: ");
      Serial.println(temperature);
      
      // Send data in the format of "M123|T12.34\n"
      client.print("I");
      client.print(id);
  
      client.print(DELIMITER);
      
      client.print("M");
      client.print(moisture);
      
      client.print(DELIMITER);
      
      client.print("T");
      client.print(temperature);
      
      client.print(DELIMITER);
      
      client.print("C");
      client.write(bmpHeader, BMP::headerSize);
      client.write(camera->frame, camera->xres * camera->yres * 2);
      
      client.println("");

      last = millis();
    }
    
    while (client.available()) { // Loop through everything before next iteration
      uint8_t identifier[1] = {0};
      client.read(identifier, 1);

      if (identifier[0] == 73) { // 73 = "I", ID
        uint8_t new_id[37] = {0};
        client.read(new_id, 36);
        Serial.print("Saving new ID: ");
        Serial.println((char *) new_id);

        id = String((char *) new_id);

        preferences.begin("probe", false); // false = Read-Write mode
        preferences.putString("id", id); // Save ID
        preferences.end();
      } else if (identifier[0] == 80) { // 80 = "P", Pest spray
        uint8_t cmd[1] = {0};
        client.read(cmd, 1);

        if (cmd[0] == 48) { // 48 = "0"
          Serial.println("P0");
          ledcWrite(4,1638);
        } else if (cmd[0] == 49) { // 49 = "1"
          Serial.println("P1");
          ledcWrite(4,7864);
        }
        
      } else if (identifier[0] == 87) { // 87 = "W", Water sprinkler
        uint8_t cmd[1] = {0};
        client.read(cmd, 1);

        if (cmd[0] == 48) { // 48 = "0"
          Serial.println("W0");
          digitalWrite(SPRINKLER_PIN, LOW);
        } else if (cmd[0] == 49) { // 49 = "1"
          Serial.println("W1");
          digitalWrite(SPRINKLER_PIN, HIGH);
        }
      }
    }
  } else if (WiFi.status() != WL_CONNECTED) {
    // (Re)Connect to WiFi network
    connectToWiFi();
    
  } else if (!client.connected()) {
    // (Re)Connect to server
    client.stop();
    connectToServer();
    delay(1000);
  }
}
