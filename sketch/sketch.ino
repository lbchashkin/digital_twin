#include <iarduino_VCC.h>

void setup() {
  Serial.begin(9600);
  pinMode(A1, INPUT);
}

void loop() {

  float VCC = analogRead_VCC(); 
  int sensorValue = analogRead(A0);
  float voltage = sensorValue * (VCC / 1023.0);

  Serial.println(VCC);
  Serial.println(voltage);
  delay(1000);
}
