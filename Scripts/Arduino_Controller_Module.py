import serial
import serial.tools.list_ports

class ArduinoController:
    ser = None
    baudRates = "500000"
    comPort = ""
    isSignalStopping = False
    detectionState = ""
    
    SensorResultDurationData =  {"Signal": [], "Temperature": [], "MagneticField": [], "VibrationX":[], "VibrationY":[], "VibrationZ":[], "Sound": []}
    SensorResultValueData = {"Signal": [], "Temperature": [], "MagneticField": [], "VibrationX":[], "VibrationY":[], "VibrationZ":[], "Sound": []}

    def CheckIfArduinoIsConnected(self):
        if self.ser == None:
            return "Arduino is not found."
        else:
            return "Arduino is connected."
        
    def OutputTextToArduino(self, text):
        self.ser.write(bytes(str(text) + "\n", 'utf-8'))
    
    def AutoSearchArduino(self):
        IsArduinoGet = False
        comNumber = None
        ports = self.GetCurrentPortsAvailable()
        selectComport = None
        if len(ports) == 0:
            self.comPort = ""
            self.ser = None
            return "Arduino is not found."
        else:
            self.comPort = ""
            for i in range(0, len(ports)):
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
    
    def GetCurrentPortsAvailable(self):
        ports = serial.tools.list_ports.comports()
        available_ports = []
        
        for port in ports:
            try:
                s = serial.Serial(port.device)
                s.close()
                available_ports.append(port.device)
            except serial.SerialException:
                pass

        return available_ports

        ##Search Arduino with port number
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
    
    def SetBaudRate(self, baudRate):
        self.baudRates = baudRate
    
    def GetComPort(self):
        return self.comPort
    
    def AppendSignalData(self, time, value):
        self.SensorResultValueData["Signal"].append(value)
        self.SensorResultDurationData["Signal"].append(time)

    def ReadDataFromArduino(self, time):
        while self.ser.in_waiting:
            data_raw = self.ser.readline()
            data = data_raw.decode()
            data = data.replace("\n", "")
            data = data.replace("\r", "")
            #print(data)
            if self.detectionState == "":    
                self.detectionState = data
                self.isSignalWriting = False
            else:
                if self.detectionState in self.SensorResultValueData:
                    try: 
                        self.SensorResultValueData[self.detectionState].append(float(data))
                        self.SensorResultDurationData[self.detectionState].append(time)
                        self.detectionState = ""
                    except:
                        self.detectionState = ""
                else: 
                    self.detectionState = data

    def ClearAllRealtimeData(self):
        self.SensorResultValueData.clear()
        self.SensorResultDurationData.clear()
        self.SensorResultDurationData =  {"Signal": [], "Temperature": [], "MagneticField": [], "VibrationX":[], "VibrationY":[], "VibrationZ":[], "Sound": []}
        self.SensorResultValueData = {"Signal": [], "Temperature": [], "MagneticField": [], "VibrationX":[], "VibrationY":[], "VibrationZ":[], "Sound": []}
