/* Version: v3.1, Created on 2023/09/18
 * Version time stamp:
 * Version 1.0 , build time 2021/08/29
 * Version 2.0 , build time 2021/09/06: enhance serial output text, increase countdown function
 * - Version 2.1 , altered time 2021/09/23: bug fix and enhance functionality
 * - Version 2.2, re-assign signal pins and add “const" for changing frequency and stimulation times
 *  
 * Version 3.0, Add Serial read with User Interface
 * - Version 3.1 Add User Interface writing stimulation pattern to Arduino
 * BAUD rate = 500000, remember to select, line separator symbol can be set to NL&CL
 * BAUD rate = 500000, remember to change baud rate, separator symbol choose NL&CL

 */

#include <Wire.h>

int freqT = 0;
int delayT = 10;
int ADXL345 = 0x53;

float X_out, Y_out, Z_out;

bool signalPause = false;
String state = "";
String str = "";
int action = 0;
String function[30]; 
int frequency[30];
unsigned long duration[30]; 
int deadTime[30];
int currentPeriod = 0;
int currentTime;
int Stime = 11; // Set stimulate times
int stimulationIndex = 0;
unsigned long resumeTime = 0;

String temperatureDetection = "";
String vibrationDetection = "";
String magneticFieldDetection = "";
String soundDetection = "";   
String functionGenerator = "";

int devicePin1 = A1; // Device out pin
int devicePin2 = A2; // Device out pin
int magneticPin = A3; // Pin for reading magnetic field sensor
int tempPin = A6; // Pin for reading temperature sensor
int SoundSensorPin = A7; // Pin for reading sound sensor
float tempValue, magneticValue, soundValue; // Temperature sensor value
float decibelLevel;

int magneticThreshold = 4000;
int temperatureThreshold = 4000;
int vibrationThreshold = 4000;
int soundThreshold = 4000;

int previousSoundValue = 0;

bool isAllStop = false;
bool isResuming = false;
bool overTemperatureThreshold = false;
bool overMagneticFieldThreshold = false;
bool overSoundThreshold = false;
bool overVibrationThreshold = false;
bool overCameraThreshold = false;
bool isDetectionOnly = false;
bool isSendingCommand = false;
bool isReverseSignalOutput = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(500000);
  
  pinMode(2,OUTPUT);//control1
  pinMode(3,OUTPUT);//control2
  pinMode(4,OUTPUT);//control3
  pinMode(5,OUTPUT);//control4
  pinMode(6,OUTPUT);//control5
  pinMode(7,OUTPUT);//control6
  
  pinMode(8,OUTPUT);//control1
  pinMode(9,OUTPUT);//control2
  pinMode(10,OUTPUT);//control3
  pinMode(11,OUTPUT);//control4
  pinMode(12,OUTPUT);//control5
  pinMode(13,OUTPUT);//control6
  pinMode(14,OUTPUT); //LED
  pinMode(tempPin, INPUT);
  pinMode(magneticPin, INPUT);
  pinMode(SoundSensorPin, INPUT);
  pinMode(devicePin1, OUTPUT);
  pinMode(devicePin2, OUTPUT);
  SignalAllLow();
}

void loop() {
  // put your main code here, to run repeatedly:
  while (!Serial.available()) {}
  if (Serial.available()) {
    str = Serial.readStringUntil('\n');
    if (state == ""){
      if(str == "Action")
      {
        state = "Action";
        Serial.println(str);
      }
      else if(str == "MagneticSystem")
      {
        state = "";
        Serial.println("SystemCheck");
      }
      else if(str == "StimulationTime")
      {
        state = "StimulationTime";
        Serial.println(str);
      }
      else if(str == "Function")
      {
        state = "Function";
        Serial.println(str);
      }
      else if(str == "Frequency")
      {
        state = "Frequency";
        Serial.println(str);
      }
      else if(str == "Duration")
      {
        state = "Duration";
        Serial.println(str);
      }
      else if(str == "DeadTime")
      {
        state = "DeadTime";
        Serial.println(str);
      }
      else if(str == "Temperature")
      {
        state = "Temperature";
        Serial.println(str);
      }
      else if(str == "Vibration")
      {
        state = "Vibration";
        Serial.println(str);
      }
      else if(str == "Sound")
      {
        state = "Sound";
        Serial.println(str);
      }
      else if(str == "Function Generator")
      {
        state = "Function Generator";
        Serial.println(str);
      }
      else if(str == "MagneticField")
      {
        state = "MagneticField";
        Serial.println(str);
      }
      else if(str == "MagneticField Threshold")
      {
        state = "MagneticField Threshold";
        Serial.println(str);
      }
      else if(str == "Temperature Threshold")
      {
        state = "Temperature Threshold";
        Serial.println(str);
      }
      else if(str == "Vibration Threshold")
      {
        state = "Vibration Threshold";
        Serial.println(str);
      }
      else if(str == "Sound Threshold")
      {
        state = "Sound Threshold";
        Serial.println(str);
      }
      else if(str == "DetectionOnly")
      {
        state = "";
        isDetectionOnly = true;
        Serial.println(str);
      }
      else if (str == "AllStop"){
        SignalAllLow();
        isAllStop = true;
        stimulationIndex = 0;
        state = "";
        Serial.println(str);
      }
      else if(str == "Pause")
      {
        SignalAllLow();
        isAllStop = true;
        state = "";
        Serial.println(str);
      }
      else if(str == "Start")
      {
        state = "";
        isAllStop = false;
        isDetectionOnly = false;
        Serial.println(str);
        isSendingCommand = false; 
        Stimulation();
      }
    }
    else if(state == "Action"){
      action = str.toInt();
      Serial.println(state);
      state = "";
    }
    else if(state == "StimulationTime"){
      Stime = str.toInt();
      Serial.println(state);
      state = "";
    }
    else if(state == "Frequency"){
       for(int i=0;i<Stime;i++){
         int index = str.indexOf(',');
         String sub_S = str.substring(0, index);
         str = str.substring(index+1, str.length());
         frequency[i] = sub_S.toInt();
      }
      Serial.println(state);
      state = "";
    }
    else if(state == "Function"){
      for(int i=0;i<Stime;i++){ 
         int index = str.indexOf(',');
         String sub_S = str.substring(0, index);
         str = str.substring(index+1, str.length());
         function[i] = sub_S;
      }
      Serial.println(state);
      state = "";
    }
    else if(state == "Duration"){
      for(int i=0;i<Stime;i++){
         int index = str.indexOf(',');
         String sub_S = str.substring(0, index);
         str = str.substring(index+1, str.length());
         duration[i] = sub_S.toInt();
      }
      Serial.println(state);
      state = "";
    }
    else if(state == "DeadTime"){
      for(int i=0;i<Stime;i++){
         int index = str.indexOf(',');
         String sub_S = str.substring(0, index);
         str = str.substring(index+1, str.length());
         deadTime[i] = sub_S.toInt();
      }
      Serial.println(state);
      state = "";
    }
    else if(state == "MagneticField"){
      magneticFieldDetection = str;
      Serial.println(state);
      state = "";
    }
    else if(state == "Temperature"){
      temperatureDetection = str;
      Serial.println(state);
      state = "";
    }
    else if(state == "Vibration"){
      vibrationDetection = str;
      Serial.println(state);
      state = "";
      if(vibrationDetection == "True"){
        Wire.begin();
        Wire.beginTransmission(ADXL345);
        Wire.write(0x2D);
        Wire.write(8);
        Wire.endTransmission();
      }
    }
    else if(state == "Sound"){
      soundDetection = str;
      Serial.println(state);
      state = "";
    }  
    else if(state == "Function Generator"){
      functionGenerator = str;
      Serial.println(state);
      state = "";
    }
    else if(state == "MagneticField Threshold"){
      magneticThreshold = str.toInt();
      Serial.println(state);
      state = "";
    }
    else if(state == "Temperature Threshold"){
      temperatureThreshold = str.toInt();
      Serial.println(state);
      state = "";
    }
    else if(state == "Vibration Threshold"){
      vibrationThreshold = str.toInt();
      Serial.println(state);
      state = "";
    }
    else if(state == "Sound Threshold"){
      soundThreshold = str.toInt();
      Serial.println(state);
      state = "";
    }
  }
  if(isDetectionOnly == true){
    Detection();
  }
}

void Freqstart(){
  if(action == 0){
    if(isReverseSignalOutput == false){
      digitalWrite(devicePin1, HIGH);
      digitalWrite(2,HIGH);//control1
      digitalWrite(4,HIGH);//control2
      digitalWrite(6,HIGH);//control3
      digitalWrite(8,HIGH);//control4
      digitalWrite(10,HIGH);//control5
      digitalWrite(12,HIGH);//control6
  
      digitalWrite(devicePin2, LOW);
      digitalWrite(3,LOW);//control1
      digitalWrite(5,LOW);//control2
      digitalWrite(7,LOW);//control3
      digitalWrite(9,LOW);//control4
      digitalWrite(11,LOW);//control5
      digitalWrite(13,LOW);//control6
      isReverseSignalOutput = true;
    }
    else{
      SignalAllLow();
      isReverseSignalOutput = false;
    }
  }
  else if(action == 1){
    if(isReverseSignalOutput == false){
      digitalWrite(devicePin1, HIGH);
      digitalWrite(2,HIGH);//control1
      digitalWrite(4,HIGH);//control2
      digitalWrite(6,HIGH);//control3
      digitalWrite(8,HIGH);//control4
      digitalWrite(10,HIGH);//control5
      digitalWrite(12,HIGH);//control6
  
      digitalWrite(devicePin2, LOW);
      digitalWrite(3,LOW);//control1
      digitalWrite(5,LOW);//control2
      digitalWrite(7,LOW);//control3
      digitalWrite(9,LOW);//control4
      digitalWrite(11,LOW);//control5
      digitalWrite(13,LOW);//control6

      isReverseSignalOutput = true;
    }
    else{
      digitalWrite(devicePin1, LOW);
      digitalWrite(2,LOW);//control1
      digitalWrite(4,LOW);//control2
      digitalWrite(6,LOW);//control3
      digitalWrite(8,LOW);//control4
      digitalWrite(10,LOW);//control5
      digitalWrite(12,LOW);//control6
  
      digitalWrite(devicePin2, HIGH);
      digitalWrite(3,HIGH);//control1
      digitalWrite(5,HIGH);//control2
      digitalWrite(7,HIGH);//control3
      digitalWrite(9,HIGH);//control4
      digitalWrite(11,HIGH);//control5
      digitalWrite(13,HIGH);//control6

      isReverseSignalOutput = false;
    }
  }
  else
  {
    digitalWrite(devicePin1, HIGH);
    digitalWrite(2,HIGH);//control1
    digitalWrite(4,HIGH);//control2
    digitalWrite(6,HIGH);//control3
    digitalWrite(8,HIGH);//control4
    digitalWrite(10,HIGH);//control5
    digitalWrite(12,HIGH);//control6
    
    digitalWrite(devicePin2, LOW);
    digitalWrite(3,LOW);//control1
    digitalWrite(5,LOW);//control2
    digitalWrite(7,LOW);//control3
    digitalWrite(9,LOW);//control4
    digitalWrite(11,LOW);//control5
    digitalWrite(13,LOW);//control6
  }
}

void SignalAllLow(){ // Both IN1 & IN2 LOW
  digitalWrite(devicePin1, LOW);
  digitalWrite(devicePin2, LOW);
  digitalWrite(2,LOW);//IN1
  digitalWrite(3,LOW);//IN1
  digitalWrite(4,LOW);//IN1
  digitalWrite(5,LOW);//IN1
  digitalWrite(6,LOW);//IN1
  digitalWrite(7,LOW);//IN1
  digitalWrite(8,LOW);//IN2
  digitalWrite(9,LOW);//IN2
  digitalWrite(10,LOW);//IN2
  digitalWrite(11,LOW);//IN2
  digitalWrite(12,LOW);//IN1
  digitalWrite(13,LOW);
}

void Stimulation(){
  while(stimulationIndex <= Stime) {           // Start stimulation, stimulate 5 times, each time for 30 seconds, rest for 1 minute, stimulation frequency 10Hz
    unsigned long int detectionTiming = 0;
    unsigned long int stimulationTiming = 0;
    unsigned long int tCheck = 0;
    detectionTiming = millis();
    stimulationTiming = detectionTiming;
    tCheck = detectionTiming + (duration[stimulationIndex]*1000);
    delayT = deadTime[stimulationIndex];
    freqT = 500/frequency[stimulationIndex];
    while(millis() <= tCheck){
      if(millis() >= detectionTiming){
        Detection();
        detectionTiming = millis() + 50;
      }
      if(isAllStop == true){
        break;
      }
      if(function[stimulationIndex] == "1"){
        if(overCameraThreshold == false && overMagneticFieldThreshold == false && overSoundThreshold == false && overTemperatureThreshold == false && overVibrationThreshold == false){
          if(millis()>= stimulationTiming){
            Freqstart();
            stimulationTiming = millis() + freqT;

            if(millis() >= detectionTiming - 50){
              Detection();
            }
          }
          else if(millis()>= stimulationTiming - delayT && delayT != 0){
            SignalAllLow();
          }
        }
        else
        {
          SignalAllLow();
        }
      }
      else{
        SignalAllLow();
      }
    }
    
    if(isAllStop == true){
      break;
    }
    else{
      stimulationIndex+= 1;
    }
  }
  SignalAllLow();
}

void Detection(){
    if(temperatureDetection == "True"){
       Serial.println("Temperature");
       tempValue = (((analogRead(tempPin)/ 1024.0)* 5)  - 0.5) * 100; //conversion from voltage to temperature, the resolution of the sensor is 10 mV per degree, in addition, you should use an offset of 500 mV 
       Serial.println(tempValue);
       if(isDetectionOnly == false){
         if(tempValue > temperatureThreshold){
            overTemperatureThreshold = true;
         }
         else
         {
            overTemperatureThreshold = false;
         }
       }
    }
    
    if(soundDetection == "True"){
      float voltageValue,dbValue;
      voltageValue = analogRead(SoundSensorPin) / 1024.0 * 5.0;
      soundValue = voltageValue * 50.0;  //convert voltage to decibel value
      Serial.println("Sound");
      Serial.println(soundValue);
      if(isDetectionOnly == false){
        if(soundValue > soundThreshold)
        {
          overSoundThreshold = true;
        }
        else
        {
          overSoundThreshold = false;
        }
      }
    }
    
    if(vibrationDetection == "True"){
      Wire.beginTransmission(ADXL345);
      Wire.write(0x32); // Start with register 0x32 (ACCEL_XOUT_H)
      Wire.endTransmission(false);
      Wire.requestFrom(ADXL345, 6, true);
      X_out = ( Wire.read()| Wire.read() << 8);
      X_out = X_out/256;
      Y_out = ( Wire.read()| Wire.read() << 8);
      Y_out = Y_out/256;
      Z_out = ( Wire.read()| Wire.read() << 8);
      Z_out = Z_out/256;
      
      Serial.println("VibrationX");
      Serial.println(X_out);
      Serial.println("VibrationY");
      Serial.println(Y_out);
      Serial.println("VibrationZ");
      Serial.println(Z_out);
      if(isDetectionOnly == false){
        if(X_out > vibrationThreshold || Y_out > vibrationThreshold ||Z_out > vibrationThreshold)
        {
          overVibrationThreshold = true;
        }
        else
        {
          overVibrationThreshold = false;
        }
      }
    }
    
    if(magneticFieldDetection == "True"){
      Serial.println("MagneticField");
      magneticValue = (map(analogRead(magneticPin), 102, 922, -640, 640)+15)*0.125;
      Serial.println(magneticValue);
      if(isDetectionOnly == false){
        if(magneticValue > magneticThreshold){
          overMagneticFieldThreshold = true;
        }
        else
        {
          overMagneticFieldThreshold = false;
        }
      }
    }
    
    while (Serial.available()) {
      str = Serial.readStringUntil('\n');
      if(str == "StopSignal"){
        SignalAllLow();
        overCameraThreshold = true;
        Serial.println(str);
      }
      else if(str == "StartSignal"){
        overCameraThreshold = false;
        Serial.println(str);
      }
      else if (str == "AllStop"){
        SignalAllLow();
        isAllStop = true;
        stimulationIndex = 0;
        state = "";
        Serial.println(str);
      }
      else if(str == "Pause")
      {
        SignalAllLow();
        isAllStop = true;
        state = "";
      }
      else if(str == "Start")
      {
        state = "";
        isAllStop = false;
        isDetectionOnly = false;
        Serial.println("Begin");
        isSendingCommand = false; 
        Stimulation();
      }
    }
}
