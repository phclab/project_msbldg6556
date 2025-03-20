class StimulationProtocol:
    _stepData = []
    _functionData = []
    _durationData= [] 
    _frequencyData = []
    _deadTimeData = []

    _actionIndex = 0
    _totalDuration = 0

    def GetStepData(self):
        return self._stepData

    def GetFunctionData(self):
        _functionDataString = ""
        for i in range(0,len(self._functionData)):
            if self._functionData[i] == "Stimulation":
                _functionDataString += str(1)+","
            else:
                _functionDataString += str(0)+","
        return self._functionData, _functionDataString
    
    def GetDurationData(self):
        _durationDataString = ""
        for i in range(0,len(self._functionData)):
            _durationDataString += str(self._durationData[i])+","
        return self._durationData, _durationDataString
    
    def GetFrequencyData(self):
        _frequencyDataString = ""
        for i in range(0,len(self._functionData)):
            _frequencyDataString += str(self._frequencyData[i])+","
        return self._frequencyData, _frequencyDataString
    
    def GetDeadTimeData(self):
        _deadTimeDataString = ""
        for i in range(0,len(self._functionData)):
            _deadTimeDataString += str(self._deadTimeData[i])+","
        return self._deadTimeData, _deadTimeDataString
    
    def GetAction(self):
        return self._actionIndex
    
    def GetTotalDuration(self):
        return self._totalDuration
    

    def AppendStepData(self, data:list):
        self._stepData.extend(data)
        
    def DeleteLastStepData(self):
        del(self._stepData[-1])

    def ChangeOneOfTheStepData(self, index, value):
        self._stepData[index] = value
        
    def AppendFunctionData(self, data:list):
        self._functionData.extend(data)
    
    def ChangeOneOfTheFunctionData(self, index, value):
        self._functionData[index] = value
    
    def ChangeOneOfTheDurationData(self, index, value):
        self._durationData[index] = value

    def AppendDurationData(self, data:list):
        self._durationData.extend(data)
    
    def ChangeOneOfTheFrequencyData(self, index, value):
        self._frequencyData[index] = value

    def AppendFrequencyData(self, data:list):
        self._frequencyData.extend(data)
    
    def ChangeOneOfTheDeadTimeData(self, index, value):
        self._deadTimeData[index] = value

    def AppendDeadTimeData(self, data:list):
        self._deadTimeData.extend(data)

    def SetAction(self, action:int):
        self._actionIndex = action
    
    def SetTotalDuration(self, duration:int):
        self._totalDuration = duration

    ### Make the protocol back to the default one
    def RenewToDefaultData(self):
        self.ClearAllData()
        self.SetAction(0)
        self.AppendStepData(["Step 1","Step 2","Step 3","Step 4","Step 5","Step 6","Step 7","Step 8","Step 9","Step 10"])
        self.AppendFunctionData(["Rest"]*10)
        self.AppendDurationData([30]*10)
        self.AppendFrequencyData([1]*10)
        self.AppendDeadTimeData([0]*10)

    ### Clear the protocol
    def ClearAllData(self):
        self._stepData.clear()
        self._functionData.clear()
        self._durationData.clear()
        self._frequencyData.clear()
        self._deadTimeData.clear()

    ### Add new column in the protocol
    def AddNewColumnData(self):
        self._stepData.append("Step"+str(len(self._stepData)+1))
        self._functionData.append("Rest")
        self._durationData.append(30) 
        self._frequencyData.append(1)
        self._deadTimeData.append(0)
    
    ### Delete the last column in the protocol
    def DeleteLastColumnData(self):
        del(self._stepData[-1])
        del(self._functionData[-1])
        del(self._durationData[-1])
        del(self._frequencyData[-1])
        del(self._deadTimeData[-1])
