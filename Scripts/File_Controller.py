import glob
import os
from datetime import datetime
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDir

class FileController:
    _systemController = None
    _cwd = os.getcwd()
    _lastestProtocolFolder = r'\lastest protocol' 
    _fileType = r'\*csv'

    def SetFilePath(self, cwd):
        os.chdir(cwd)
        self._cwd = os.getcwd()

    def SetSystemController(self, controller):
        self._systemController = controller

    def AutoSearchLastestParameters(self):
        files = glob.glob(self._cwd + self._lastestProtocolFolder + self._fileType)
        if len(files) != 0:
            maxFile = max(files, key=os.path.getmtime)
            readFile = pd.read_csv(maxFile)
            return True, readFile
        else:
            return False, ""
        
    def SaveLastestParameters(self, isSensorChangeSignal, magneticSensor, temperatureSensor, vibrationSensor, soundSensor, magneticThreshold, temperatureThreshold, vibrationThreshold, soundThreshold, cameraSensor, contourColor, currentBehaviorType, currentAreaTriggerType, leftCameraThreshold, rightCameraThreshold, action, stepList, functionData, durationData, frequencyData, deadTimeData):
        if not os.path.exists(self._cwd + self._lastestProtocolFolder):
            os.makedirs(self._cwd + self._lastestProtocolFolder)
        pd.DataFrame({'Is Sensor Change Signal or not': isSensorChangeSignal,
                      'Is Magnetic Sensor Open': magneticSensor,
                      'Is Temperature Sensor Open': temperatureSensor,
                      'Is Vibration Sensor Open': vibrationSensor,
                      'Is Sound Sensor Open': soundSensor,
                      'Is Camera Sensor Open': cameraSensor,
                      'Magnetic Field Threshold': magneticThreshold,
                      'Temperature Threshold': temperatureThreshold,
                      'Vibration Threshold': vibrationThreshold,
                      'Sound Threshold': soundThreshold,
                      'Camera Background Color': contourColor, 
                      'Behavior Type': currentBehaviorType, 
                      'Area Trigger Type': currentAreaTriggerType,
                      'Left(Light Area) Camera Threshold': leftCameraThreshold,
                      'Right Camera Threshold': rightCameraThreshold,
                      'Action': action,
                      'Step': stepList,
                      'Function': functionData,
                      'Duration': durationData,
                      'Frequency':frequencyData,
                      'Dead Time':deadTimeData
                      }).to_csv(self._cwd + self._lastestProtocolFolder +"/"+"Last Protocol Setting.csv")

    ##Load Stimulation Protocol
    def LoadStimulationProtocolFile(self, uiController):
        fileNameChoose, filetype = QtWidgets.QFileDialog.getOpenFileName(uiController,  "Load File",  self._cwd, "All Files (*);;Text Files (*.csv)")
        if fileNameChoose != "":
            file = pd.read_csv (fileNameChoose)
            uiController.SetStopMessage("Success.")
            return file
        else:
            uiController.SetStopMessage("You didn't choose any file")

    def SaveStimulationProtocolFile(self, uiController, isSensorChangeSignal, contourColor, currentBehaviorType, currentAreaTriggerType, action, stepList, functionData, durationData, frequencyData, deadTimeData):
        try:
            fileNameChoose, filetype = QtWidgets.QFileDialog.getSaveFileName(uiController,  
                                        "Save File",  
                                        self._cwd, # 起始路徑
                                        "All Files (*);;Text Files (*.csv)") 
            if fileNameChoose == "":
                uiController.SetStopMessage("You didn't write any file.")
            else:
                pd.DataFrame({'Is Sensor Change Signal or not': pd.Series(isSensorChangeSignal), 
                      'Camera Background Color': pd.Series(contourColor), 
                      'Behavior Type': pd.Series(currentBehaviorType), 
                      'Area Trigger Type': pd.Series(currentAreaTriggerType), 
                      'Action': pd.Series(action), 
                      'Step': pd.Series(stepList),
                      'Function': pd.Series(functionData),
                      'Duration': pd.Series(durationData),
                      'Frequency':pd.Series(frequencyData),
                      'Dead Time':pd.Series(deadTimeData)
                      }).to_csv(fileNameChoose)
                uiController.SetStopMessage("Success.")
        except PermissionError:
           uiController.SetStopMessage("Permission denied.")
    
    def SaveCameraResultsFile(self, frameThatMouseStayedInTheChamber, whichAreaMouseStayedDuringStimulation , leftChamberStayedDuration, middleChamberStayedDuration, rightChamberStayedDuration, stimulationDuration):
        pd.DataFrame({'Mouse Stay Area Timeline':pd.Series(frameThatMouseStayedInTheChamber), 
                      'Mouse Stay Area':pd.Series(whichAreaMouseStayedDuringStimulation), 
                      'Duration in Left Area(s)':pd.Series(leftChamberStayedDuration), 
                      'Duration in Middle Area(s)':pd.Series(middleChamberStayedDuration), 
                      'Duration in Right Area(s)':pd.Series(rightChamberStayedDuration)}
                      ).to_csv(self._cwd+"/"+datetime.now().strftime("%Y%m%d_%H%M%S")+"_Camera Result.csv")
    
    def SaveStimulationResultsFile(self, timeline, signal, magneticTimeline, magneticValue, temperatureTimeline, temperatureValue, vibrationXTimeline, vibrationXValue,vibrationYTimeline, vibrationYValue, vibrationZTimeline, vibrationZValue, soundTimeline, soundValue):
        pd.DataFrame({'Timeline':pd.Series(timeline), 
                      'Stimulaition': pd.Series(signal), 
                      'Magnetic Field Timeline': pd.Series(magneticTimeline), 
                      'Magnetic Field': pd.Series(magneticValue), 
                      'Temperature Timeline': pd.Series(temperatureTimeline), 
                      'Temperature': pd.Series(temperatureValue), 
                      'VibtrationX Timeline': pd.Series(vibrationXTimeline), 
                      'VibationX': pd.Series(vibrationXValue), 
                      'VibtrationY Timeline': pd.Series(vibrationYTimeline), 
                      'VibationY': pd.Series(vibrationYValue), 
                      'VibtrationZ Timeline': pd.Series(vibrationZTimeline), 
                      'VibationZ': pd.Series(vibrationZValue), 
                      'Sound Timeline':pd.Series(soundTimeline), 
                      'Sound':pd.Series(soundValue) 
                     }).to_csv(self._cwd+"/"+datetime.now().strftime("%Y%m%d_%H%M%S")+"_Stimulation Result.csv")


    def LoadVideoFile(self, uiController):
        file, filetype = QtWidgets.QFileDialog.getOpenFileName(uiController, "Open Movie", QDir.homePath())
        if file != "" :   
            uiController.SetCameraUIPreCalculationStatus()
            self._systemController.videoController.SetVideoPreCalculationStatus(file)
        else:
            uiController.SetStopMessage("You didn't choose any file.")

    def SelectFolder(self):
        folderPath = QtWidgets.QFileDialog.getExistingDirectory()
        if folderPath:
            self._cwd = folderPath