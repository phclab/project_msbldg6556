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
        ports = self.GetCurrentPortsAvailable()
        if len(ports) == 0:
            self.comPort = ""
            self.ser = None
            return "Arduino is not found."
        elif len(ports) > 1:
            self.comPort = ports[0]
            self.ser = serial.Serial(self.comPort , self.baudRates, timeout=0.5)
            return "Multiple Arduino is found. The first one is selected."
        else: 
            self.comPort = ports[0]
            self.ser = serial.Serial(self.comPort , self.baudRates, timeout=0.5)
            return "Arduino " + self.comPort + " is found."
    
    def GetCurrentPortsAvailable(self):
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.name)
        return ports

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