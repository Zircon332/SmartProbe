#include <Arduino.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include <SPI.h>
#include <stdio.h>
#include <stdlib.h>
#include <WiFi.h>

#include "Config.h"

#define WIFI_TIMEOUT_MS 20000
#define MOISTURE_PIN 4
#define TEMPERATURE_PIN 2

IPAddress server(address[0], address[1], address[2], address[3]);
WiFiClient client;

OneWire oneWire(TEMPERATURE_PIN);
DallasTemperature sensorTemperature(&oneWire);

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
  sensorTemperature.begin();
}

void loop() {
  // Read sensor values
  int moisture = analogRead(MOISTURE_PIN);
  sensorTemperature.requestTemperatures();
  
  Serial.print("Moisture: ");
  Serial.println(moisture);

  Serial.print("Temperature: ");
  Serial.println(sensorTemperature.getTempCByIndex(0));
  
//  if (WiFi.status() == WL_CONNECTED && client.connected()) {
//    //Do something
//    Serial.println("Connected");
//  } else if (WiFi.status() != WL_CONNECTED) {
//    // (Re)Connect to WiFi network
//    connectToWiFi();
//  } else if (!client.connected()) {
//    // (Re)Connect to server
//    client.stop();
//    connectToServer();
//    delay(1000);
//  }
}
