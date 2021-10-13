#include <Arduino.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include <SPI.h>
#include <stdio.h>
#include <stdlib.h>
#include <WiFi.h>
#include <ESP32Servo.h>

#include "BMP.h"
#include "Config.h"
#include "OV7670.h"

#define WIFI_TIMEOUT_MS 20000

#define SPRAYER_PIN 5
#define SPRINKLER_PIN 18

#define MOISTURE_PIN 39
#define TEMPERATURE_PIN 23

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

Servo pestServo;

const char* DELIMITER = "!#)%@#^#$]";
unsigned char bmpHeader[BMP::headerSize];

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

  camera = new OV7670(OV7670::Mode::QQVGA_RGB565, SIOD, SIOC, VSYNC, HREF, XCLK, PCLK, D0, D1, D2, D3, D4, D5, D6, D7);
  BMP::construct16BitHeader(bmpHeader, camera->xres, camera->yres);

  pestServo.setPeriodHertz(50);
  pestServo.attach(SPRAYER_PIN, 500, 2400);

  digitalWrite(SPRAYER_PIN,HIGH);
}

void loop() {
  // Read sensor values
  int moisture = analogRead(MOISTURE_PIN);
  
  sensorTemperature.requestTemperatures();
  float temperature = sensorTemperature.getTempCByIndex(0);

  camera->oneFrame();
  
  
  Serial.print("Moisture: ");
  Serial.println(moisture);

  Serial.print("Temperature: ");
  Serial.println(temperature);
  
  if (WiFi.status() == WL_CONNECTED && client.connected()) {
    if (client.available() >= 2 ){
      uint8_t cmd[2] = {0};
      //Serial.println("Client available");
      client.read(cmd,2);
      String str = (char*)cmd;
      Serial.println(str);

      // Water Sprinkler (Pump)
      if (str.charAt(0) == 'W'){
        if(str.charAt(1) == '0'){
          digitalWrite(SPRINKLER_PIN,LOW);
        }else{
          digitalWrite(SPRINKLER_PIN,HIGH);
        }
      }
      
      // Pest Spray (Servo)
      if (str.charAt(0) == 'P'){
        if(str.charAt(1) == '0'){
          pestServo.write(0);
        }else{
          pestServo.write(180);
        }
      }
    }
    
    //print(cmd);
    // Send data in the format of "M123|T12.34\n"
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
    
  } else if (WiFi.status() != WL_CONNECTED) {
    // (Re)Connect to WiFi network
    connectToWiFi();
  } else if (!client.connected()) {
    // (Re)Connect to server
    client.stop();
    connectToServer();
    delay(1000);
  }

  delay(10000);
}
