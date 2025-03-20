import serial
import serial.tools.list_ports
from time import time

class ArduinoController:
    ser = None
    baudRates = "500000"
    comPort = ""
    isSignalStopping = False
    detectionState = ""
    
    ### Dictionary to store the sensor value
    SensorResultDurationData =  {"Signal": [], "Temperature": [], "MagneticField": [], "VibrationX":[], "VibrationY":[], "VibrationZ":[], "Sound": []}
    SensorResultValueData = {"Signal": [], "Temperature": [], "MagneticField": [], "VibrationX":[], "VibrationY":[], "VibrationZ":[], "Sound": []}

    ### Check if any Arduino is connected
    def CheckIfArduinoIsConnected(self):
        if self.ser == None:
            return "Arduino is not found."
        else:
            return "Arduino is connected."
    
    ### Output text to Arduino
    def OutputTextToArduino(self, text):
        self.ser.write(bytes(str(text) + "\n", 'utf-8'))
    
    ### Auto search Arduino that can be connected
    def AutoSearchArduino(self):
        IsArduinoGet = False
        comNumber = None
        ports = self.GetCurrentPortsAvailable()
        selectComport = None
        if len(ports) == 0:
            self.comPort = ""
            self.ser = None
            return "Arduino is not found."
        elif len(ports) > 1:
            self.comPort = ""
            for i in range(0, len(ports)):
                try:
                    self.comPort = ports[i]
                    self.ser = serial.Serial(self.comPort , self.baudRates, timeout=0.5)
                    checkPoint = ""
                    checkTime = 0
                    while checkPoint != "SystemCheck" and IsArduinoGet == False:
                        if checkTime != 10:
                            self.OutputTextToArduino("MagneticSystem")
                            data_raw = self.ser.readline()
                            data = data_raw.decode()
                            data = data.replace("\n", "")
                            data = data.replace("\r", "")
                            checkPoint = data
                            if checkPoint == "SystemCheck":
                                IsArduinoGet = True
                            else:
                                checkTime += 1
                        else:
                            break
                    if comNumber == None and checkPoint == "SystemCheck":
                        comNumber = i
                        selectComport = ports[comNumber]
                except:
                    pass
            if comNumber != None:
                try:
                    self.ser = None
                    self.comPort = selectComport
                    self.ser = serial.Serial(self.comPort , self.baudRates, timeout=0.5)
                    return "Arduino is found. The "+ str(self.comPort) +" is selected."
                except:
                    return "The "+ str(self.comPort) +" cannot be connected. Please check the Arduino."
            else:
                return "Arduino is not found."
        else: 
            self.comPort = ports[0]
            self.ser = serial.Serial(self.comPort , self.baudRates, timeout=0.5)
            return "Arduino " + self.comPort + " is found."
    
    ### Get available ports
    def GetCurrentPortsAvailable(self):
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.name)
        return ports

    ### Search Arduino with port number
    def SetComPortAndSearchArduino(self, text):     
        try:
            comPort = str(text)
            self.ser = serial.Serial(comPort, self.baudRates, timeout= 0.5)
            self.comPort = comPort
            return "Arduino is connected to Arduino " + self.comPort + "."
        except serial.SerialException:
            if self.ser != None:
                self.comPort = self.ser.port
                return "Arduino "+ comPort + " is not found. Reconnect to Arduino " + self.comPort + "."
            else:
                return "Arduino is not found."
    
    ### Set baud rate
    def SetBaudRate(self, baudRate):
        self.baudRates = baudRate
    
    ### Get the comport of the connected Arduino
    def GetComPort(self):
        return self.comPort
    
    ### Store signal data
    def AppendSignalData(self, time, value):
        self.SensorResultValueData["Signal"].append(value)
        self.SensorResultDurationData["Signal"].append(time)

    ### Get data from Arduino
    def ReadDataFromArduino(self, startTime):
        while self.ser.in_waiting:
            currentTime = time() - startTime
            data_raw = self.ser.readline()
            data = data_raw.decode()
            data = data.replace("\n", "")
            data = data.replace("\r", "")
            #print(data)
            try:               
                key, value = data.split(":")
                if key in self.SensorResultValueData:
                    self.SensorResultValueData[key].append(float(value)) 
                    self.SensorResultDurationData[key].append(currentTime)
            except ValueError:
                pass
            
            '''if self.detectionState == "":    
                self.detectionState = data
            else:
                if self.detectionState in self.SensorResultValueData:
                    try: 
                        self.SensorResultValueData[self.detectionState].append(float(data))
                        self.SensorResultDurationData[self.detectionState].append(currentTime)
                        self.detectionState = ""
                    except:
                        self.detectionState = ""
                else: 
                    self.detectionState = data'''

    ### Clear all the data stored from Arduino
    def ClearAllRealtimeData(self):
        self.SensorResultValueData.clear()
        self.SensorResultDurationData.clear()
        self.SensorResultDurationData =  {"Signal": [], "Temperature": [], "MagneticField": [], "VibrationX":[], "VibrationY":[], "VibrationZ":[], "Sound": []}
        self.SensorResultValueData = {"Signal": [], "Temperature": [], "MagneticField": [], "VibrationX":[], "VibrationY":[], "VibrationZ":[], "Sound": []}
