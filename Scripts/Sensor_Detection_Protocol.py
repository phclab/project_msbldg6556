class SensorDetectionProtocol:
    _isSensorChangeSignal = False

    _isSensorOpenData = {"Temperature": False, "MagneticField": False, "Vibration": False, "Sound": False}
    _sensorThresholdData = {"Temperature": 4000, "MagneticField": 4000, "Vibration": 4000, "Sound": 4000}   

    ### Set if the signal change with sensor value
    def ReverseTheVauleOfIsSensorChangeSignal(self):
        self._isSensorChangeSignal = not self._isSensorChangeSignal
    
    ### Get if the signal change with sensor value
    def GetTheVauleOfIsSensorChangeSignal(self):
        return self._isSensorChangeSignal

    #Sensor opening Setting
    def SetSensorOpenData(self, sensorType:str, isOpen:bool):
        self._isSensorOpenData[sensorType] = isOpen
    
    #Sensor threshod Setting
    def SetSensorThresholdData(self, sensorType:str, threshold):
        self._sensorThresholdData[sensorType] = threshold
    
    def GetAllSensorOpenData(self):
        return self._isSensorOpenData

    def GetAllSensorThresholdData(self):
        return self._sensorThresholdData

    #Sensor opening Getting
    def GetSensorOpenData(self, sensorType:str):
        return self._isSensorOpenData[sensorType]
    
    #Sensor threshod Getting
    def GetSensorThresholdData(self, sensorType:str):
        return self._sensorThresholdData[sensorType] 
