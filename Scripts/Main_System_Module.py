import Arduino_Controller_Module
import File_Management_Module
import Stimulation_Protocol 
import Sensor_Detection_Protocol
import Video_Module
import pandas as pd
import threading
from time import sleep, time

class SystemController:
    stimulationProtocol = Stimulation_Protocol.StimulationProtocol()
    sensorDetectionProtocol = Sensor_Detection_Protocol.SensorDetectionProtocol()
    arduinoController = Arduino_Controller_Module.ArduinoController()
    fileController = File_Management_Module.FileController()
    videoController = Video_Module.VideoController()
    uiController = None
    isSignalStopping = False
    isSensorReadingStarted = False
    isCameraReadingStarted = False
    sensorReadingState = "SensorReading"
    startTime = 0

    def GetTheCurrentTime(self):
        return time()
    
    def __init__(self, parent = None):
        self.fileController.SetSystemController(self)
        self.videoController.SetSystemController(self)
        self._CameraThread = threading.Thread(target= self.ReadCameraRealtime)
        self._eventCamera = threading.Event()
        self._SignalReadingThread = threading.Thread(target= self.ReadSensorValueRealtime)
        self._eventSignal = threading.Event()

    ### Start the sensor detection
    def StartSignalReadingThread(self):
        self._eventSignal.set()
        if self._SignalReadingThread.is_alive() == False:
            self._SignalReadingThread.start()

    ### Start the stimulation
    def StartSystemTimeCounting(self):
        self._eventSignal.set()
        self.startTime = time()
        self.arduinoController.OutputTextToArduino("Start")
        self.videoController.isResultVideoRecording = False

    ### Start the camera detection
    def SetCameraReadingStarted(self):
        self.isCameraReadingStarted = True
        self._eventCamera.set()
        self._CameraThread.start()

    def GetTimeDurationAfterStart(self):
        return time()-self.startTime

    def SetUIController(self, uiConroller):
        self.uiController = uiConroller

    ### Get UI Controller
    def GetUIController(self):
        return self.uiController
    
    ### Get Arduino Controller
    def GetArduinoController(self):
        return self.arduinoController

    ### Add new column in the protocol
    def AddNewColumn(self):
        self.stimulationProtocol.AddNewColumnData()
        self.uiController.AddRightColumnInProtocolTable(index = -1)

    ### Get sensor timing list
    def GetTimelineData(self, sensorType):
        return self.arduinoController.SensorResultDurationData[sensorType]

    ### Get sensor value list
    def GetValueData(self, sensorType):
        return self.arduinoController.SensorResultValueData[sensorType]

    ### Get the protocol file and set the protocol GUI value with the file
    def LoadFileAndSetProtocolParameter(self):
        file = self.fileController.LoadStimulationProtocolFile(self.uiController)
        self.uiController.ClearAllProtocolTable()
        self.stimulationProtocol.ClearAllData()
        self.stimulationProtocol.AppendStepData(file['Step'])
        self.stimulationProtocol.AppendFunctionData(file['Function'])
        self.stimulationProtocol.AppendDurationData(file['Duration'])
        self.stimulationProtocol.AppendFrequencyData(file['Frequency'])
        self.stimulationProtocol.AppendDeadTimeData(file['Dead Time'])
        self.uiController.CompareDataToCurrentColumnLength(len(self.stimulationProtocol.GetStepData()))
        self.uiController.RenewPlot(self.uiController._plot)
        self.uiController.ChangeAllTheContentInTheProtocol()

    ### Output stimualtion setting to Arduino
    def OutputStimulationSettingToArduino(self):
        if self._CameraThread.is_alive():
            self._eventCamera.wait()
        self._eventSignal.clear()
        self.uiController.ChangeAllTheContentInTheProtocol()
        self.uiController.DisableStimulationPage()
        
        for i in range(0, len(self.uiController._functionButton)):    
            self.stimulationProtocol.ChangeOneOfTheDurationData(i, self.uiController._timeButton[i].value())
            self.stimulationProtocol.ChangeOneOfTheFrequencyData(i, self.uiController._frequencyButton[i].value())
            self.stimulationProtocol.ChangeOneOfTheDeadTimeData(i, self.uiController._deadTimeButton[i].value())
            self.stimulationProtocol.ChangeOneOfTheFunctionData(i, self.uiController._functionButton[i].currentText())
        if self.arduinoController.CheckIfArduinoIsConnected() == "Arduino is not found.":
            self.uiController.SetStopMessage(self.arduinoController.CheckIfArduinoIsConnected())
        else:
            _textToOutput = {
                "Action":str(self.stimulationProtocol.GetAction()), 
                "StimulationTime": str(len(self.stimulationProtocol.GetFunctionData()[0])),
                "Function": self.stimulationProtocol.GetFunctionData()[1],
                "Frequency":self.stimulationProtocol.GetFrequencyData()[1],
                "Duration":self.stimulationProtocol.GetDurationData()[1],
                "DeadTime":self.stimulationProtocol.GetDeadTimeData()[1],
                }
            self.OutputTextAndCheckIsSend(textToOutput= _textToOutput, suffix= "")
            _textToOutput = self.sensorDetectionProtocol.GetAllSensorOpenData()
            self.OutputTextAndCheckIsSend(textToOutput= _textToOutput, suffix= "")
            _textToOutput = self.sensorDetectionProtocol.GetAllSensorThresholdData()
            self.OutputTextAndCheckIsSend(textToOutput= _textToOutput, suffix= " Threshold")
            
            self.uiController.SetStopMessage("The program is updated.")
        self.uiController.AbleStimulationPage()
        self.uiController.RenewPlot(self.uiController.stimulationProtocolPlot)
        self.uiController.RenewPlot(self.uiController.stimulationProtocolPlotInCameraPage)
        self.isSensorReadingStarted = True
        self._eventSignal.set()
        if self._SignalReadingThread._started.is_set() == False:
            self._SignalReadingThread.start()

    ### Output text to Arduino and check if Arduino gets the text
    def OutputTextAndCheckIsSend(self, textToOutput, suffix):
        for i in textToOutput.keys():
            checkPoint = ""
            while checkPoint != str(i + suffix):
                self.arduinoController.OutputTextToArduino(i + suffix)
                data_raw = self.arduinoController.ser.readline()
                data = data_raw.decode()
                data = data.replace("\n", "")
                data = data.replace("\r", "")
                checkPoint = data
            checkPoint = ""
            while checkPoint != str(i + suffix):
                self.arduinoController.OutputTextToArduino(textToOutput[i])
                data_raw = self.arduinoController.ser.readline()
                data = data_raw.decode()
                data = data.replace("\n", "")
                data = data.replace("\r", "")
                checkPoint = data

    ### Load lastest stimulation protocol and put in GUI
    def SetLastestParametersWithCsvFile(self, isPreviousFileExist,  csvFile):
        if isPreviousFileExist == False:
            self.uiController.SetStopMessage("There is no last time setting protocol.")
            self.stimulationProtocol.RenewToDefaultData()
        else:
            self.stimulationProtocol.ClearAllData()
            self.stimulationProtocol.SetAction(csvFile['Action'].tolist()[0])
            self.stimulationProtocol.AppendStepData(csvFile['Step'].tolist())
            self.stimulationProtocol.AppendFunctionData(csvFile['Function'].tolist())
            self.stimulationProtocol.AppendDurationData(csvFile['Duration'].tolist())
            self.stimulationProtocol.AppendFrequencyData(csvFile['Frequency'].tolist())
            self.stimulationProtocol.AppendDeadTimeData(csvFile['Dead Time'].tolist())
            self.sensorDetectionProtocol._isSensorChangeSignal = csvFile['Is Sensor Change Signal or not'].tolist()[0]
            self.sensorDetectionProtocol.SetSensorOpenData("MagneticField", csvFile['Is Magnetic Sensor Open'].tolist()[0])
            self.sensorDetectionProtocol.SetSensorOpenData("Temperature", csvFile['Is Temperature Sensor Open'].tolist()[0])
            self.sensorDetectionProtocol.SetSensorOpenData("Vibration", csvFile['Is Vibration Sensor Open'].tolist()[0])
            self.sensorDetectionProtocol.SetSensorOpenData("Sound", csvFile['Is Sound Sensor Open'].tolist()[0])
            self.sensorDetectionProtocol.SetSensorThresholdData("MagneticField", csvFile['Magnetic Field Threshold'].tolist()[0])
            self.sensorDetectionProtocol.SetSensorThresholdData("Temperature", csvFile['Temperature Threshold'].tolist()[0])
            self.sensorDetectionProtocol.SetSensorThresholdData("Vibration", csvFile['Vibration Threshold'].tolist()[0])
            self.sensorDetectionProtocol.SetSensorThresholdData("Sound", csvFile['Sound Threshold'].tolist()[0])
            self.videoController._isCameraChangeSignal = csvFile['Is Camera Sensor Open'].tolist()[0]
            self.videoController._miceDetectColor = csvFile['Camera Background Color'].tolist()[0]
            self.videoController._leftContourThreshold = csvFile['Left(Light Area) Camera Threshold'].tolist()[0]
            self.videoController._rightContourThreshold = csvFile['Right Camera Threshold'].tolist()[0]
            self.videoController._currentBehaviorString = csvFile['Behavior Type'].tolist()[0]

    ### Save lastest stimulation protocol to csv file
    def SaveLastestParametersToCsvFile(self):
        self.fileController.SaveLastestParameters(
            isSensorChangeSignal = self.sensorDetectionProtocol.GetTheVauleOfIsSensorChangeSignal(),
            magneticSensor = self.sensorDetectionProtocol.GetSensorOpenData("MagneticField"), 
            temperatureSensor = self.sensorDetectionProtocol.GetSensorOpenData("Temperature"), 
            vibrationSensor = self.sensorDetectionProtocol.GetSensorOpenData("Vibration"), 
            soundSensor  = self.sensorDetectionProtocol.GetSensorOpenData("Sound"),
            cameraSensor = self.videoController._isCameraChangeSignal,
            magneticThreshold  = self.sensorDetectionProtocol.GetSensorThresholdData("MagneticField"),
            temperatureThreshold = self.sensorDetectionProtocol.GetSensorThresholdData("Temperature"), 
            vibrationThreshold  = self.sensorDetectionProtocol.GetSensorThresholdData("Vibration"),
            soundThreshold = self.sensorDetectionProtocol.GetSensorThresholdData("Sound") ,
            contourColor = self.videoController.GetContourDetectColor(), 
            currentBehaviorType = self.videoController.GetCurrentBehaviorString(), 
            currentAreaTriggerType = self.videoController.GetCurrentAreaTriggerType(),
            leftCameraThreshold = self.videoController._leftContourThreshold,
            rightCameraThreshold = self.videoController._rightContourThreshold,
            action = self.stimulationProtocol.GetAction(), 
            stepList = self.stimulationProtocol.GetStepData(), 
            functionData = self.stimulationProtocol.GetFunctionData()[0], 
            durationData = self.stimulationProtocol.GetDurationData()[0], 
            frequencyData = self.stimulationProtocol.GetFrequencyData()[0], 
            deadTimeData = self.stimulationProtocol.GetDeadTimeData()[0])
    
    ### Save stimulation protocol to csv file
    def SaveStimulationProtocolToCsvFile(self, uiController):
        self.uiController.ChangeAllTheContentInTheProtocol()
        self.fileController.SaveStimulationProtocolFile(
            uiController = uiController,
            isSensorChangeSignal = self.sensorDetectionProtocol.GetTheVauleOfIsSensorChangeSignal(),
            contourColor = self.videoController.GetContourDetectColor(),
            currentBehaviorType = self.videoController.GetCurrentBehaviorString(),
            currentAreaTriggerType = self.videoController.GetCurrentAreaTriggerType(),
            action = self.stimulationProtocol.GetAction(),
            stepList = self.stimulationProtocol.GetStepData(),
            functionData = self.stimulationProtocol.GetFunctionData()[0],
            durationData = self.stimulationProtocol.GetDurationData()[0],
            frequencyData = self.stimulationProtocol.GetFrequencyData()[0],
            deadTimeData= self.stimulationProtocol.GetDeadTimeData()[0]
            )

    ### Save camera results to csv file
    def SaveCameraResultsToCsvFile(self):
        self.fileController.SaveCameraResultsFile(
            frameThatMouseStayedInTheChamber = self.videoController.GetFrameThatMouseStayedInTheChamber(), 
            whichAreaMouseStayedDuringStimulation =  self.videoController.GetWhichAreaMouseStayedDuringStimulation(),
            stimulationDuration = self.stimulationProtocol.GetTotalDuration(), 
            leftChamberStayedDuration = self.videoController.CalculateTheDurationThatMiceStayedInEachArea(totalDuration= self.stimulationProtocol.GetTotalDuration())[0], 
            middleChamberStayedDuration = self.videoController.CalculateTheDurationThatMiceStayedInEachArea(totalDuration= self.stimulationProtocol.GetTotalDuration())[1], 
            rightChamberStayedDuration = self.videoController.CalculateTheDurationThatMiceStayedInEachArea(totalDuration= self.stimulationProtocol.GetTotalDuration())[2])

    ### Save stimulation results to csv file
    def SaveStimulationResultsToCsvFile(self):
        self.fileController.SaveStimulationResultsFile(
            timeline = self.arduinoController.SensorResultDurationData["Signal"], 
            signal = self.arduinoController.SensorResultValueData["Signal"], 
            magneticTimeline = self.arduinoController.SensorResultDurationData["MagneticField"], 
            magneticValue = self.arduinoController.SensorResultValueData["MagneticField"], 
            temperatureTimeline = self.arduinoController.SensorResultDurationData["Temperature"], 
            temperatureValue = self.arduinoController.SensorResultValueData["Temperature"], 
            vibrationXTimeline = self.arduinoController.SensorResultDurationData["VibrationX"], 
            vibrationXValue = self.arduinoController.SensorResultValueData["VibrationX"],
            vibrationYTimeline = self.arduinoController.SensorResultDurationData["VibrationY"], 
            vibrationYValue = self.arduinoController.SensorResultValueData["VibrationY"], 
            vibrationZTimeline = self.arduinoController.SensorResultDurationData["VibrationZ"], 
            vibrationZValue = self.arduinoController.SensorResultValueData["VibrationZ"], 
            soundTimeline = self.arduinoController.SensorResultDurationData["Sound"], 
            soundValue = self.arduinoController.SensorResultValueData["Sound"])

    ### Start Arduino Stimulation
    def StartStimulation(self):
        if self.arduinoController.ser == None:
            self.uiController.SetStopMessage("Arduino is not found.")
        else:
            self.arduinoController.ClearAllRealtimeData()
            self.arduinoController.OutputTextToArduino("Start")

    ### Start sensor detection 
    def ReadSensorValueRealtime(self):
        while self.isSensorReadingStarted == True:
            self._eventSignal.wait()
            if self.sensorReadingState == "SensorReading":
                if self.arduinoController.ser != None:
                    self.arduinoController.ReadDataFromArduino(self.startTime)

    ### Start camera detection
    def ReadCameraRealtime(self):
        while self.isCameraReadingStarted == True:
            self.videoController.RepeatVideoCycle(cwd= self.fileController._cwd)
    
    ### Stimulation signal changed with camera 
    def SignalChangeWithCamera(self):
        if self.videoController._isCameraChangeSignal == True:
            if self.videoController.GetStimulationStateWithMicePosition() == True:
                self.sensorReadingState = "SensorWriting"
                self.arduinoController.OutputTextToArduino("StartSignal")
                self.isSignalStopping = False
            else:
                self.sensorReadingState = "SensorWriting"
                self.arduinoController.OutputTextToArduino("StopSignal")
                self.isSignalStopping = True

            self.sensorReadingState = "SensorReading"
