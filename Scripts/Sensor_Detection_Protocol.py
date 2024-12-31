class SensorDetectionProtocol:
    _isSensorChangeSignal = False

    _isSensorOpenData = {"Temperature": False, "MagneticField": False, "Vibration": False, "Sound": False}
    _sensorThresholdData = {"Temperature": 4000, "MagneticField": 4000, "Vibration": 4000, "Sound": 4000}   

    
    def ReverseTheVauleOfIsSensorChangeSignal(self):
        self._isSensorChangeSignal = not self._isSensorChangeSignal
    
    def GetTheVauleOfIsSensorChangeSignal(self):
        return self._isSensorChangeSignal

    #Sensor Standard Setting and Getting
    def SetSensorOpenData(self, sensorType:str, isOpen:bool):
        self._isSensorOpenData[sensorType] = isOpen
    
    def SetSensorThresholdData(self, sensorType:str, threshold):
        self._sensorThresholdData[sensorType] = threshold
    
    def GetAllSensorOpenData(self):
        return self._isSensorOpenData

    def GetAllSensorThresholdData(self):
        return self._sensorThresholdData

    def GetSensorOpenData(self, sensorType:str):
        return self._isSensorOpenData[sensorType]
    
    def GetSensorThresholdData(self, sensorType:str):
        return self._sensorThresholdData[sensorType] 