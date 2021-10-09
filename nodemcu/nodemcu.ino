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
#define SPRAYER_PIN 5
#define SPRINKLER_PIN 18

IPAddress server(address[0], address[1], address[2], address[3]);
WiFiClient client;

OneWire oneWire(TEMPERATURE_PIN);
DallasTemperature sensorTemperature(&oneWire);

const char* DELIMITER = "|";

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
  digitalWrite(SPRAYER_PIN,HIGH);
}

void loop() {
  // Read sensor values
  int moisture = analogRead(MOISTURE_PIN);
  sensorTemperature.requestTemperatures();
  float temperature = sensorTemperature.getTempCByIndex(0);
  
  
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

      int pin = SPRINKLER_PIN;
      if (str.charAt(0) == 'P'){
        pin = SPRAYER_PIN;
      }

      if(str.charAt(1) == '0'){
        digitalWrite(pin,LOW);
      }else{
        digitalWrite(pin,HIGH);
      }
    }
    
    //print(cmd);
    // Send data in the format of "M123|T12.34\n"
    client.print("M");
    client.print(moisture);
    client.print(DELIMITER);
    client.print("T");
    client.print(temperature);
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
}
