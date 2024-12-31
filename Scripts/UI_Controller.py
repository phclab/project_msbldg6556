from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph
import pyqtgraph.exporters
import sys
import System_Controller
import numpy as np

class UIController(QWidget):
    app = QApplication([])
    _rowHeader = []
    _columnHeader = ["Action","Duration(sec)","Frequency(Hz)", "Dead Time(millisecond)"]
    _functionCategory = ["Rest", "Stimulation"]
    _actionCategory = ["On-Off", "Bidirection", "Always On"]
    _behaviorType = ["Light Dark Box", "Place Preference Test"]
    _colorType = ["White Background, Black Mice", "Black Background, White Mice"]
    _lightDarkBoxTriggerType = ["Stop stimulation while mice in the ROI.", "Start stimulation while mice in the ROI."]
    _placePreferenceTriggerType = ["Stop stimulation while mice in the left chamber.", "Start stimulation while mice in the left chamber.", "Stop stimulation while mice in the right chamber.", "Start stimulation while mice in the right chamber."]
    _sensorChangeSignalType = ["Don't Stop signal while over threshold","Stop signal while over threshold"]
    
    _sensorCheckbox = {}
    _sensorRealtimePlot = {}
    _currentOpenSensorCheckbox = {}
    _currentOpenSensorRealtimePlot = {}
    _pageData = {}

    _actionButton = []
    _functionButton = []
    _timeButton = []
    _frequencyButton = []
    _deadTimeButton = []
    _geometry = app.desktop().availableGeometry()
    systemController = None

    _tab = QTabWidget()
    _contentFont = QFont()
    _contentFont.setPointSize(12)
    _tabFont = QFont()
    _tabFont.setPointSize(16)
    _tab.setFont(_tabFont)
    _tab.resize(_geometry.size())
    _titleFont = QFont()
    _titleFont.setPointSize(28)

    _timer = QTimer()
    _realtimePlotTimer = QTimer()

    _increment = 0
    _currentStep = 0
    totalDuration = 0
    _currentDuration = 0
    lastIndex = 0

    def __init__(self, parent = None):
        super(UIController, self).__init__(parent)
        self.systemController = System_Controller.SystemController()
        self.systemController.SetUIController(self)
        self.AssembleUI()
        self.systemController.SetLastestParametersWithCsvFile(isPreviousFileExist= self.systemController.fileController.AutoSearchLastestParameters()[0], csvFile= self.systemController.fileController.AutoSearchLastestParameters()[1])
        self.SetUIWithLastestParameters()
        self.ChangeBehaviorType(dropdown=self.behaviorTypeDropDown)
        self.ChangeContourDetectType(dropdown= self.contourDetectTypeDropdown)
        self.CompareDataToCurrentColumnLength(len(self.systemController.stimulationProtocol.GetStepData()))
        self.RenewPlot(self._plot)

    ### 組合各種UI內容
    def AssembleUI(self):
        self.setGeometry(self._geometry)
        self.setWindowTitle("Ecosystem")
        self.SetStimulationPage()
        self.SetSensorPage()
        self.SetCameraPage()
        self.SetStimulationRealtimePage()


        ###Setting Stimulation Program Page
        for key in self._pageData:
            self._tab.addTab(self._pageData[key], key)

        self.mainLayout = QGridLayout(self)
        self.mainLayout.addWidget(self._tab)
        self.SetStopMessage(self.systemController.arduinoController.AutoSearchArduino())

    ### 關閉刺激頁面
    def DisableStimulationPage(self):
        self._toolBar.setDisabled(True)
        for i in range(0, len(self._actionButton)):
            self._actionButton[i].setDisabled(True)
        self._protocolTable.setDisabled(True)

    ### 開啟刺激頁面
    def AbleStimulationPage(self):
        self._toolBar.setDisabled(False)
        for i in range(0, len(self._actionButton)):
            self._actionButton[i].setDisabled(False)
        self._protocolTable.setDisabled(False)

    ### 錯誤訊息
    def SetStopMessage(self, message):
        self.stopMessage = QMessageBox.about(self,"Hint Message", message)
    
    ### 改變刺激型態
    def ChangeActionValue(self, value):
        self.systemController.stimulationProtocol.SetAction(value)

    ### 設定刺激頁面
    def SetStimulationPage(self):
        ####Setting Action Button
        _settingPage = QWidget(self)
        self._plot = pyqtgraph.plot()
        self._plot.setBackground("w")
        self._pageData["Protocol"] = _settingPage

        _actionLabel = QLabel("【Stimulation Mode】")
        self._actionButton.append(QRadioButton("On-Off"))
        self._actionButton.append(QRadioButton("Bidirection"))
        self._actionButton.append(QRadioButton("Always On"))

        self._actionButton[0].toggled.connect(lambda:self.ChangeActionValue(0))
        self._actionButton[0].toggled.connect(lambda:self.RenewPlot(self._plot))
        self._actionButton[1].toggled.connect(lambda:self.ChangeActionValue(1))
        self._actionButton[1].toggled.connect(lambda:self.RenewPlot(self._plot))
        self._actionButton[2].toggled.connect(lambda:self.ChangeActionValue(2))
        self._actionButton[2].toggled.connect(lambda:self.RenewPlot(self._plot))
        self._actionButton[0].setChecked(True)

        ####Setting ToolBar
        self._toolBarLayout = QVBoxLayout()
        self._toolBarLayoutContol = QWidget()
        self._toolBar = QToolBar()
        self._toolBar.setStyleSheet("background-color : gray")
        self._toolBar.setIconSize(QSize(100, 100))
        
        self._newButton = QAction('New File')
        self._toolBar.addAction(self._newButton)
        self._newButton.triggered.connect(lambda: self.RenewProtocolTableToBlank())
        self._newButton.setFont(self._tabFont)
        self._toolBar.addSeparator()
        
        self._saveButton = QAction('Save File')
        self._toolBar.addAction(self._saveButton)
        self._saveButton.setShortcut("Ctrl+S")
        self._saveButton.triggered.connect(lambda: self.systemController.SaveStimulationProtocolToCsvFile(uiController= self))
        self._saveButton.setFont(self._tabFont)
        self._toolBar.addSeparator()

        self._loadButton = QAction('Load File')
        self._toolBar.addAction(self._loadButton)
        self._loadButton.triggered.connect(lambda:self.systemController.LoadFileAndSetProtocolParameter())
        self._loadButton.setFont(self._tabFont)
        self._toolBar.addSeparator()
        
        self._addColumnButton = QAction('Add a new Column')
        self._toolBar.addAction(self._addColumnButton)
        self._addColumnButton.triggered.connect(self.systemController.AddNewColumn)
        self._addColumnButton.triggered.connect(lambda:self.RenewPlot(self._plot))
        self._addColumnButton.setFont(self._tabFont)
        self._toolBar.addSeparator()

        self._removeColumnButton = QAction('Remove Last Column')
        self._toolBar.addAction(self._removeColumnButton)
        self._removeColumnButton.triggered.connect(self.RemoveRightColumnInProtocolTable)
        self._removeColumnButton.setFont(self._tabFont)
        self._removeColumnButton.triggered.connect(lambda:self.RenewPlot(self._plot))

        self._toolBar.addSeparator()
        self._arduinoSettingButton = QAction('Search Arduino')
        self._toolBar.addAction(self._arduinoSettingButton)
        self._arduinoSettingButton.setFont(self._tabFont)
        self._arduinoSettingButton.triggered.connect(lambda: self.ChooseArduinoPort())
        
        self._toolBarLayout.addWidget(self._toolBar)
        self._toolBarLayoutContol.setLayout(self._toolBarLayout)


        self.filePathLabel = QLabel("【File Path】" + str(self.systemController.fileController._cwd))
        self.filePathButton = QPushButton("Choose Address")
        self.filePathButton.clicked.connect(self.systemController.fileController.SelectFolder)
        self.filePathButton.clicked.connect(lambda: self.filePathLabel.setText("【File Path】" + str(self.systemController.fileController._cwd)))
        ####Setting Period Sheets
        self._protocolTable = QTableWidget()
        self._protocolTable.setRowCount(len(self._columnHeader))
        self._protocolTable.setColumnCount(len(self.systemController.stimulationProtocol.GetStepData()))

        self._protocolTable.setHorizontalHeaderLabels(self._rowHeader)
        self._protocolTable.setVerticalHeaderLabels(self._columnHeader)
        self._protocolTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._protocolTable.setMaximumHeight(250)

        ####Setting Stimulation Period Plot
        self.settingLayout = QGridLayout(self)
        self._plot.showGrid(x = True, y = True)
        self._plot.setLabel('left', '<span style="color: black; font-size: 28px">Output(High-Low)</span>')
        self._plot.setLabel('bottom', '<span style="color: black; font-size: 28px">Time(sec)</span>')
        self._plot.setYRange(0, 2, padding= 1, update=True)
        self._plot.setMouseEnabled(x=True, y=False)
        self._plot.enableAutoRange(y=False)

        self.firstLayout = QHBoxLayout(self)
        self.firstLayoutControl = QWidget()
        self.firstLayoutControl.setLayout(self.firstLayout)
        for i in range(0,len(self._actionButton)):
            self.firstLayout.addWidget(self._actionButton[i])

        self.settingLayout.addWidget(self._toolBarLayoutContol, 0, 0, 1, 2)
        self.settingLayout.addWidget(self.filePathLabel, 1, 0, 1, 1)
        self.settingLayout.addWidget(self.filePathButton, 1, 1, 1, 1)
        self.settingLayout.addWidget(_actionLabel, 2, 0, 1, 2)
        self.settingLayout.addWidget(self.firstLayoutControl, 3, 0, 1, 2)
        self.settingLayout.addWidget(self._protocolTable, 4, 0, 1, 2)
        self.settingLayout.addWidget(self._plot, 5, 0, 1, 2)
        _settingPage.setLayout(self.settingLayout)

    
    ### 設定感測器頁面
    def SetSensorPage(self):
        _sensorPage = QWidget(self)
        self._pageData["Sensor"] = _sensorPage

         ####Setting Detection Checkbox
        self.sensorChangeSignalDropDown = QComboBox(self)
        self.sensorChangeSignalDropDown.addItems(self._sensorChangeSignalType)

        self.magneticFieldDetectionCheckBox = QCheckBox('Magnetic Field Detection', self)
        self.magneticFieldDetectionCheckBox.clicked.connect(lambda: self.systemController.sensorDetectionProtocol.SetSensorOpenData("MagneticField", self.magneticFieldDetectionCheckBox.isChecked()))
        self.magneticFieldThresholdInputField = QLineEdit(self)
        self.magneticFieldThresholdInputField.setValidator(QIntValidator())
        self.magneticFieldThresholdInputFieldTitle = QLabel("Threshold(mT)")
        self.magneticFieldThresholdInputField.setText("4000")
        self.magneticFieldThresholdInputField.textChanged.connect(lambda: self.systemController.sensorDetectionProtocol.SetSensorThresholdData(sensorType="MagneticField", threshold=int(self.magneticFieldThresholdInputField.text())))
        
        self.temperatureDetectionCheckBox = QCheckBox('Temperature Detection', self)
        self.temperatureDetectionCheckBox.clicked.connect(lambda: self.systemController.sensorDetectionProtocol.SetSensorOpenData("Temperature", self.temperatureDetectionCheckBox.isChecked()))
        self.temperatureThresholdInputField = QLineEdit(self)
        self.temperatureThresholdInputField.setValidator(QIntValidator())
        self.temperatureThresholdInputFieldTitle = QLabel("Threshold(Celsius)")
        self.temperatureThresholdInputField.setText("25")
        self.temperatureThresholdInputField.textChanged.connect(lambda: self.systemController.sensorDetectionProtocol.SetSensorThresholdData(sensorType="Temperature", threshold=int(self.temperatureThresholdInputField.text())))
        
        self.vibrationDetectionCheckBox = QCheckBox('Vibration Detection', self)
        self.vibrationDetectionCheckBox.clicked.connect(lambda: self.systemController.sensorDetectionProtocol.SetSensorOpenData("Vibration", self.vibrationDetectionCheckBox.isChecked()))
        self.vibrationThresholdInputField = QLineEdit(self)
        self.vibrationThresholdInputField.setValidator(QIntValidator())
        self.vibrationThresholdInputFieldTitle = QLabel("Threshold(cm/s2)")
        self.vibrationThresholdInputField.setText("25")
        self.vibrationThresholdInputField.textChanged.connect(lambda: self.systemController.sensorDetectionProtocol.SetSensorThresholdData(sensorType="Vibration", threshold=int(self.vibrationThresholdInputField.text())))
        
        self.soundDetectionCheckBox = QCheckBox('Sound Detection', self)
        self.soundDetectionCheckBox.clicked.connect(lambda: self.systemController.sensorDetectionProtocol.SetSensorOpenData("Sound", self.soundDetectionCheckBox.isChecked()))
        self.soundThresholdInputField = QLineEdit(self)
        self.soundThresholdInputField.setValidator(QIntValidator())
        self.soundThresholdInputFieldTitle = QLabel("Threshold(dB)")
        self.soundThresholdInputField.setText("30")
        self.soundThresholdInputField.textChanged.connect(lambda: self.systemController.sensorDetectionProtocol.SetSensorThresholdData(sensorType="Sound", threshold=int(self.soundThresholdInputField.text())))

        self.sensorLayout = QGridLayout(self)
        self.sensorLayout.addWidget(self.sensorChangeSignalDropDown, 0, 0, 1, 6)
        self.sensorLayout.addWidget(self.magneticFieldDetectionCheckBox, 1, 0)
        self.sensorLayout.addWidget(self.magneticFieldThresholdInputFieldTitle, 1, 1)
        self.sensorLayout.addWidget(self.magneticFieldThresholdInputField , 1, 2)
        self.sensorLayout.addWidget(self.temperatureDetectionCheckBox, 1, 3)
        self.sensorLayout.addWidget(self.temperatureThresholdInputFieldTitle, 1, 4)
        self.sensorLayout.addWidget(self.temperatureThresholdInputField , 1, 5)
        self.sensorLayout.addWidget(self.vibrationDetectionCheckBox, 2, 0)
        self.sensorLayout.addWidget(self.vibrationThresholdInputFieldTitle, 2, 1)
        self.sensorLayout.addWidget(self.vibrationThresholdInputField , 2, 2)
        self.sensorLayout.addWidget(self.soundDetectionCheckBox, 2, 3)
        self.sensorLayout.addWidget(self.soundThresholdInputFieldTitle, 2, 4)
        self.sensorLayout.addWidget(self.soundThresholdInputField , 2, 5)

        _sensorPage.setLayout(self.sensorLayout)
        _sensorPage.resize(self._geometry.width(), self._geometry.height())


    ### 設定相機頁面
    def SetCameraPage(self):
        _cameraPage = QWidget(self)
        self._pageData["Camera"] = _cameraPage

        self._cameraToolBarLayout = QVBoxLayout()
        self._cameraToolBarLayoutContol = QWidget()
        self._cameraToolBar = QToolBar()
        self._cameraToolBar.setStyleSheet("background-color : gray")
        self._cameraToolBar.setIconSize(QSize(100, 100))

        self.playVideoButton = QAction('Play Video')
        self._cameraToolBar.addAction(self.playVideoButton)
        self.playVideoButton.triggered.connect(lambda: self.systemController.videoController.CheckIfVideoIsAbled())
        self.playVideoButton.triggered.connect(lambda:self.RenewPlot(self._plot))
        self.playVideoButton.setFont(self._tabFont)

        self.loadVideoButton = QAction("Load Video File", self)
        self._cameraToolBar.addAction(self.loadVideoButton)
        self.loadVideoButton.triggered.connect(lambda: self.systemController.fileController.LoadVideoFile(self))
        self.loadVideoButton.setFont(self._tabFont)

        self.clearPointButton = QAction("Clear Detection ROI", self)
        self.clearPointButton.triggered.connect(lambda: self.systemController.videoController.ResetDetectArea())
        self._cameraToolBar.addAction(self.clearPointButton)
        self.clearPointButton.setFont(self._tabFont)

        self.mediaStopButton = QAction("Stop Detection System", self)
        self.mediaStopButton.setEnabled(False)
        self.mediaStopButton.triggered.connect(lambda: self.StopVideo())
        self._cameraToolBar.addAction(self.mediaStopButton)
        self.mediaStopButton.setFont(self._tabFont)

        self.frameLabel = QLabel(self)
        self.frameRightLabel = QLabel(self)
        self.contourRightLabel = QLabel(self)
        self.frameLabelLayout = QHBoxLayout(self)
        self.frameLabelLayout.addWidget(self.frameLabel, 0)
        self.frameLabelLayout.addWidget(self.frameRightLabel, 1)
        self.frameLabelGroup = QWidget()
        self.frameLabelGroup.setLayout(self.frameLabelLayout)

        ####Purpose : Setting Stimulation Protocol Plot
        self.stimulationProtocolPlotInCameraPage = pyqtgraph.plot()
        self.stimulationProtocolPlotInCameraPage.setBackground("w")
        self.stimulationProtocolPlotInCameraPage.showGrid(x = True, y = True)
        self.stimulationProtocolPlotInCameraPage.setLabel('left', 'Output(High-Low)') # <font>&mu;</font>
        self.stimulationProtocolPlotInCameraPage.setLabel('bottom', 'Time(sec)') # <math>sin(x)
        self.stimulationProtocolPlotInCameraPage.setYRange(0, 2, padding= 1, update=True)
        self.stimulationProtocolPlotInCameraPage.setMouseEnabled(x=False, y=True)
        self.stimulationProtocolPlotInCameraPage.enableAutoRange(y=False)
        
        ####Purpose : Setting Realtime Singal Plot
        self.realSignalPlotInCameraPage = pyqtgraph.plot()
        self.realSignalPlotInCameraPage.setBackground("w")
        self.realSignalPlotInCameraPage.showGrid(x = True, y = True)
        self.realSignalPlotInCameraPage.setLabel('left', 'Output(High-Low)')
        self.realSignalPlotInCameraPage.setLabel('bottom', 'Time(sec)')
        self.realSignalPlotInCameraPage.setYRange(0, 2, padding= 1, update=True)
        self.realSignalPlotInCameraPage.setMouseEnabled(x=False, y=True)
        self.realSignalPlotInCameraPage.enableAutoRange(y=False)

        self.contourPlot = pyqtgraph.plot()
        self.contourPlot.setBackground("w")
        self.contourPlot.showGrid(x = True, y = True)
        self.contourPlot.setLabel('left', 'Chamber') # <font>&mu;</font>
        self.contourPlot.setLabel('bottom', 'Time(sec)') # <math>sin(x)
        self.contourPlot.setYRange(-2, 2, padding= 1, update=True)
        self.contourPlot.setMouseEnabled(x=False, y=True)
        self.contourPlot.enableAutoRange(y=False)
        
        self.contourPixelsLabel = QLabel(self)
        self.contourPixelsLabel.setText("Pixels Number: 0")
        self.contourPixelsLabel.setFont(self._contentFont)
        self.leftContourThresholdInputField = QLineEdit(self)
        self.leftContourThresholdInputField.setValidator(QIntValidator())
        self.leftContourThresholdInputField.setFont(self._contentFont)
        self.leftSuggestedContourThresholdTitle = QLabel("Left Threshold of Pixels Number", self)
        self.leftSuggestedContourThresholdTitle.setFont(self._contentFont)

        self.contourDetectTypeDropdown = QComboBox(self)
        self.contourDetectTypeDropdown.addItems(self._lightDarkBoxTriggerType)
        self.contourDetectTypeDropdown.setFont(self._contentFont)
        self.contourDetectTypeDropdown.currentIndexChanged.connect(lambda: self.ChangeContourDetectType(dropdown=self.contourDetectTypeDropdown))
        self.behaviorTypeDropDown = QComboBox(self)
        self.behaviorTypeDropDown.addItems(self._behaviorType)
        self.behaviorTypeDropDown.setFont(self._contentFont)
        self.behaviorTypeDropDown.currentIndexChanged.connect(lambda: self.ChangeBehaviorType(dropdown=self.behaviorTypeDropDown))

        self.leftContourColorDropdown = QComboBox(self)
        self.leftContourColorDropdown.addItems(self._colorType)
        self.leftContourColorDropdown.setFont(self._contentFont)
        self.leftContourThresholdInputField.setText(str(self.systemController.videoController.GetLeftContourThreshold()))
        self.leftContourThresholdInputField.textChanged.connect(lambda: self.systemController.videoController.SetLeftContourThreshold(value = int(self.leftContourThresholdInputField.text())))

        self.rightContourPixelsLabel = QLabel(self)
        self.rightContourPixelsLabel.setText("Right Pixels Number: 0")
        self.rightContourPixelsLabel.setFont(self._contentFont)
        self.rightContourThresholdInputField = QLineEdit(self)
        self.rightContourThresholdInputField.setValidator(QIntValidator())
        self.rightContourThresholdInputField.setFont(self._contentFont)
        self.rightContourThresholdInputField.setText(str(self.systemController.videoController.GetRightContourThreshold()))
        self.rightContourThresholdInputField.textChanged.connect(lambda: self.systemController.videoController.SetRightContourThreshold(value = int(self.rightContourThresholdInputField.text())))
        self.areaStayDurationText =  QLabel("Duration(L/R):", self)
        self.areaStayDurationText.setFont(self._contentFont)
        self.rightSuggestedContourThresholdTitle = QLabel("Right Threshold of Pixels Number", self)
        self.rightSuggestedContourThresholdTitle.setFont(self._contentFont)
        
        self.stimulationStateLabel = QLabel("Not Stimulation",self)
        self.stimulationStateLabel.setFont(self._contentFont)
        
        
        self.mediaLayout = QGridLayout(self)
        self.mediaLayout.addWidget(self._cameraToolBar, 0,0,1,4)
        self.mediaLayout.addWidget(self.behaviorTypeDropDown,1,0)
        self.mediaLayout.addWidget(self.leftContourColorDropdown,2,0)
        self.mediaLayout.addWidget(self.contourDetectTypeDropdown,3,0)

        self.mediaLayout.addWidget(self.leftSuggestedContourThresholdTitle,2,2)
        self.mediaLayout.addWidget(self.leftContourThresholdInputField,3,2)
        
        self.mediaLayout.addWidget(self.rightSuggestedContourThresholdTitle,2,3)
        self.mediaLayout.addWidget(self.rightContourThresholdInputField,3,3)        

        self.mediaLayout.addWidget(self.stimulationStateLabel,4,0)
        self.mediaLayout.addWidget(self.areaStayDurationText,4,1)
        self.mediaLayout.addWidget(self.contourPixelsLabel,4,2)
        self.mediaLayout.addWidget(self.rightContourPixelsLabel,4,3)

        self.mediaLayout.addWidget(self.stimulationProtocolPlotInCameraPage,5,0)
        self.mediaLayout.addWidget(self.realSignalPlotInCameraPage,6,0)
        self.mediaLayout.addWidget(self.contourPlot,7,0)
        self.mediaLayout.addWidget(self.frameLabelGroup, 5,2,3,2)

        _cameraPage.setLayout(self.mediaLayout)
        _cameraPage.resize(self._geometry.width(), self._geometry.height())


    ### 設定實時刺激畫面
    def SetStimulationRealtimePage(self):
        ##Realtime Stimulation Page
        _realtimePage = QWidget(self)
        self._pageData["Stimulation"] = _realtimePage
        self.realtimeMainLayout = QGridLayout(self)

        self.buttonLayout = QHBoxLayout(self)
        self.buttonLayoutControl = QWidget()
        self.buttonLayoutControl.setLayout(self.buttonLayout)
        self.startButton = QPushButton("Start")
        self.startButton.setFont(self._titleFont)
        self.startButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.startButton.clicked.connect(lambda: self.StartSystem())
        self.startButton.setIconSize(QSize(100,100))

        self.stopButton = QPushButton("Stop")
        self.stopButton.setFont(self._titleFont)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.clicked.connect(lambda: self.StopSystem())
        self.stopButton.setDisabled(True)
        self.stopButton.setIconSize(QSize(100,100))
        self.buttonLayout.addWidget(self.startButton)
        self.buttonLayout.addWidget(self.stopButton)

        ####Purpose : Setting Stimulation Protocol Plot
        self.stimulationProtocolPlot = pyqtgraph.plot()
        self.stimulationProtocolPlot.setBackground("w")
        self.stimulationProtocolPlot.showGrid(x = True, y = True)
        self.stimulationProtocolPlot.setLabel('left', 'Output(High-Low)') # <font>&mu;</font>
        self.stimulationProtocolPlot.setLabel('bottom', 'Time(sec)') # <math>sin(x)
        self.stimulationProtocolPlot.setYRange(0, 2, padding= 1, update=True)
        self.stimulationProtocolPlot.setMouseEnabled(x=False, y=True)
        self.stimulationProtocolPlot.enableAutoRange(y=False)
        self.StimulationProtocolPlotShowCheckBox = QCheckBox()
        self.StimulationProtocolPlotShowCheckBox.setText("Stimulation Protocol Plot")
        self.StimulationProtocolPlotShowCheckBox.setFont(self._tabFont)
        self.StimulationProtocolPlotShowCheckBox.setChecked(True)
        self.StimulationProtocolPlotShowCheckBox.stateChanged.connect(lambda: self.stimulationProtocolPlot.setHidden(not self.StimulationProtocolPlotShowCheckBox.isChecked()))
        
        ####Purpose : Setting Realtime Singal Plot
        self.realSignalPlot = pyqtgraph.plot()
        self.realSignalPlot.setBackground("w")
        self.realSignalPlot.showGrid(x = True, y = True)
        self.realSignalPlot.setLabel('left', 'Output(High-Low)')
        self.realSignalPlot.setLabel('bottom', 'Time(sec)')
        self.realSignalPlot.setYRange(0, 2, padding= 1, update=True)
        self.realSignalPlot.setMouseEnabled(x=False, y=True)
        self.realSignalPlot.enableAutoRange(y=False)
        self._sensorRealtimePlot["Signal"] = self.realSignalPlot

        self.realSignalPlotShowCheckBox = QCheckBox()
        self.realSignalPlotShowCheckBox.setText("Realtime Signal Plot")
        self.realSignalPlotShowCheckBox.setFont(self._tabFont)
        self.realSignalPlotShowCheckBox.setChecked(True)
        self.realSignalPlotShowCheckBox.stateChanged.connect(lambda: self.realSignalPlot.setHidden(not self.realSignalPlotShowCheckBox.isChecked()))
        self._sensorCheckbox["Signal"] = self.realSignalPlotShowCheckBox

        ####Purpose : Setting Magnetic Field Plot
        self.realtimeMagneticFieldPlot = pyqtgraph.plot()
        self.realtimeMagneticFieldPlot.setBackground("w")
        self.realtimeMagneticFieldPlot.showGrid(x = True, y = True)
        self.realtimeMagneticFieldPlot.setYRange(0, 80, padding= 1, update=True)
        self.realtimeMagneticFieldPlot.setMouseEnabled(x=False, y=True)
        self.realtimeMagneticFieldPlot.enableAutoRange(y=True)
        self._sensorRealtimePlot["MagneticField"] = self.realtimeMagneticFieldPlot

        self.realMagneticFieldPlotShowCheckBox = QCheckBox()
        self.realMagneticFieldPlotShowCheckBox.setText("Magnetic Field")
        self.realMagneticFieldPlotShowCheckBox.setFont(self._tabFont)
        self.realMagneticFieldPlotShowCheckBox.setChecked(True)
        self.realMagneticFieldPlotShowCheckBox.stateChanged.connect(lambda: self.realtimeMagneticFieldPlot.setHidden(not self.realMagneticFieldPlotShowCheckBox.isChecked()))
        self._sensorCheckbox["MagneticField"] = self.realMagneticFieldPlotShowCheckBox

        ####Purpose : Setting Temperature Plot
        self.realtimeTemperaturePlot = pyqtgraph.plot()
        self.realtimeTemperaturePlot.setBackground("w")
        self.realtimeTemperaturePlot.showGrid(x = True, y = True)
        self.realtimeTemperaturePlot.setYRange(-30, 30, padding= 1, update=True)
        self.realtimeTemperaturePlot.setMouseEnabled(x=False, y=True)
        self.realtimeTemperaturePlot.enableAutoRange(y=True)
        self._sensorRealtimePlot["Temperature"] = self.realtimeTemperaturePlot

        self.realTemperaturePlotShowCheckBox = QCheckBox()
        self.realTemperaturePlotShowCheckBox.setText("Temperature")
        self.realTemperaturePlotShowCheckBox.setFont(self._tabFont)
        self.realTemperaturePlotShowCheckBox.setChecked(True)
        self.realTemperaturePlotShowCheckBox.stateChanged.connect(lambda: self.realtimeTemperaturePlot.setHidden(not self.realTemperaturePlotShowCheckBox.isChecked()))
        self._sensorCheckbox["Temperature"] = self.realTemperaturePlotShowCheckBox

        ####Purpose : Setting Vibration Plot
        self.realtimeVibrationPlot = pyqtgraph.plot()
        self.realtimeVibrationPlot.setBackground("w")
        self.realtimeVibrationPlot.showGrid(x = True, y = True)
        self.realtimeVibrationPlot.setYRange(0, 200, padding= 1, update=True)
        self.realtimeVibrationPlot.setMouseEnabled(x=False, y=True)
        self.realtimeVibrationPlot.enableAutoRange(y=True)
        self._sensorRealtimePlot["Vibration"] = self.realtimeVibrationPlot

        self.realVibrationPlotShowCheckBox = QCheckBox()
        self.realVibrationPlotShowCheckBox.setText("Vibration")
        self.realVibrationPlotShowCheckBox.setFont(self._tabFont)
        self.realVibrationPlotShowCheckBox.setChecked(True)
        self.realVibrationPlotShowCheckBox.stateChanged.connect(lambda: self.realtimeVibrationPlot.setHidden(not self.realVibrationPlotShowCheckBox.isChecked()))
        self._sensorCheckbox["Vibration"] = self.realVibrationPlotShowCheckBox

        ####Purpose : Setting Sound Plot
        self.realtimeSoundPlot = pyqtgraph.plot()
        self.realtimeSoundPlot.setBackground("w")
        self.realtimeSoundPlot.showGrid(x = True, y = True)
        self.realtimeSoundPlot.setYRange(0, 60, padding= 1, update=True)
        self.realtimeSoundPlot.setMouseEnabled(x=False, y=True)
        self.realtimeSoundPlot.enableAutoRange(y=True)
        self._sensorRealtimePlot["Sound"] = self.realtimeSoundPlot

        self.realSoundPlotShowCheckBox = QCheckBox()
        self.realSoundPlotShowCheckBox.setText("Sound")
        self.realSoundPlotShowCheckBox.setFont(self._tabFont)
        self.realSoundPlotShowCheckBox.setChecked(True)
        self.realSoundPlotShowCheckBox.stateChanged.connect(lambda: self.realtimeSoundPlot.setHidden(not self.realSoundPlotShowCheckBox.isChecked()))
        self._sensorCheckbox["Sound"] = self.realVibrationPlotShowCheckBox

        ####Setting ProgressBar
        self.progressbar = QProgressBar()
        
        self.realtimeMainLayout.addWidget(self.buttonLayoutControl,0,0,1,0)
        self.realtimeMainLayout.addWidget(self.progressbar,1,0,1,0)
        self.realtimeMainLayout.addWidget(self.StimulationProtocolPlotShowCheckBox, 2,0)
        self.realtimeMainLayout.addWidget(self.stimulationProtocolPlot,3,0,1,0)
        self.realtimeMainLayout.addWidget(self.realSignalPlotShowCheckBox, 4,0)
        self.realtimeMainLayout.addWidget(self.realSignalPlot,5,0,1,0)
        self.realtimeMainLayout.addWidget(self.realMagneticFieldPlotShowCheckBox,6,0)
        self.realtimeMainLayout.addWidget(self.realtimeMagneticFieldPlot,7,0)
        self.realtimeMainLayout.addWidget(self.realTemperaturePlotShowCheckBox,6,1)
        self.realtimeMainLayout.addWidget(self.realtimeTemperaturePlot,7,1)
        self.realtimeMainLayout.addWidget(self.realVibrationPlotShowCheckBox,8,0)
        self.realtimeMainLayout.addWidget(self.realtimeVibrationPlot,9,0)
        self.realtimeMainLayout.addWidget(self.realSoundPlotShowCheckBox,8,1)
        self.realtimeMainLayout.addWidget(self.realtimeSoundPlot,9,1)
        _realtimePage.setLayout(self.realtimeMainLayout)

    ##Add one column
    def AddRightColumnInProtocolTable(self, index):
        self._protocolTable.insertColumn(self._protocolTable.columnCount())
        self._rowHeader.append("Step" + str(self._protocolTable.columnCount()))
        self._functionButton.append(QComboBox())
        self._functionButton[-1].addItems(self._functionCategory)
        self._functionButton[-1].setCurrentText(self.systemController.stimulationProtocol._functionData[index])
        self._timeButton.append(QSpinBox())
        self._timeButton[len(self._timeButton)-1].setValue(self.systemController.stimulationProtocol._durationData[index])
        self._timeButton[len(self._timeButton)-1].setMaximum(10000)
        self._frequencyButton.append(QSpinBox())
        self._frequencyButton[-1].setMinimum(1)
        self._frequencyButton[-1].setValue(self.systemController.stimulationProtocol._frequencyData[index])
        self._deadTimeButton.append(QSpinBox())
        self._deadTimeButton[-1].setMaximum(100)
        self._deadTimeButton[-1].setValue(self.systemController.stimulationProtocol._deadTimeData[index])

        self._timeButton[-1].valueChanged.connect(lambda:self.RenewPlot(self._plot))
        self._functionButton[-1].currentTextChanged.connect(lambda:self.RenewPlot(self._plot))
        self._functionButton[-1].currentTextChanged.connect(lambda:self.RenewPlot(self._plot))
        self._frequencyButton[-1].valueChanged.connect(lambda:self.RenewPlot(self._plot))
        self._frequencyButton[-1].valueChanged.connect(lambda:self.RenewPlot(self._plot))
        self._deadTimeButton[-1].valueChanged.connect(lambda:self.RenewPlot(self._plot))
        self._deadTimeButton[-1].valueChanged.connect(lambda:self.RenewPlot(self._plot))

        self._protocolTable.setCellWidget(0,len(self._functionButton)-1,self._functionButton[-1])
        self._protocolTable.setCellWidget(1,len(self._timeButton)-1,self._timeButton[-1])
        self._protocolTable.setCellWidget(2,len(self._frequencyButton)-1,self._frequencyButton[-1])
        self._protocolTable.setCellWidget(3,len(self._deadTimeButton)-1,self._deadTimeButton[-1])
        self._protocolTable.setHorizontalHeaderLabels(self._rowHeader)
    

    ### 移除表格最右方資料
    def RemoveRightColumnInProtocolTable(self):
        self.systemController.stimulationProtocol.DeleteLastColumnData()
        if self._protocolTable.columnCount() == 1:
            self.SetStopMessage("The length of column can not be zero.")
        else:
            self._protocolTable.removeColumn(self._protocolTable.columnCount()-1)
            del self._rowHeader[-1]
            del self._functionButton[-1]
            del self._timeButton[-1]
            del self._frequencyButton[-1]
            del self._deadTimeButton[-1]
            self._protocolTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    

    ##Compare current data and currant table size, then add/remove the column
    def CompareDataToCurrentColumnLength(self, dataLength):
        if(dataLength > self._protocolTable.columnCount()):
            for i in range(dataLength - self._protocolTable.columnCount()):
                self.AddRightColumnInProtocolTable(index= i)
        elif(dataLength < self._protocolTable.columnCount()):
            for i in range(self._protocolTable.columnCount() - dataLength):
                self.RemoveRightColumnInProtocolTable()
    
    
    ### 將資料帶入表格中
    def ChangeAllTheContentInTheTable(self):
        operationNumber = len(self.systemController.stimulationProtocol.GetStepData())
        functionData = self.systemController.stimulationProtocol.GetFunctionData()[0]
        durationData = self.systemController.stimulationProtocol.GetDurationData()[0]
        frequencyData = self.systemController.stimulationProtocol.GetFrequencyData()[0]
        deadTimeData = self.systemController.stimulationProtocol.GetDeadTimeData()[0]
        for index in range(0, operationNumber):
            self._functionButton[index].setCurrentText(functionData[index])
            self._timeButton[index].setValue(durationData[index])
            self._frequencyButton[index].setValue(frequencyData[index])
            self._deadTimeButton[index].setValue(deadTimeData[index])
        
        self.RenewPlot(self._plot)

    ### 將表格內容存入資料
    def ChangeAllTheContentInTheProtocol(self):
        for index in range(0, len(self._rowHeader)):
            self.systemController.stimulationProtocol._functionData[index] = self._functionButton[index].currentText()
            self.systemController.stimulationProtocol._durationData[index] = self._timeButton[index].value()
            self.systemController.stimulationProtocol._frequencyData[index] = self._frequencyButton[index].value()
            self.systemController.stimulationProtocol._deadTimeData[index] = self._deadTimeButton[index].value()

    ##Update stimulation plot
    def CalculateTheSignalPlot(self):
        y = [0]
        x0 = [0]
        for i in range(0, len(self._functionButton)):
            if self._functionButton[i].currentText() == "Rest":
                self._frequencyButton[i].setDisabled(True)
                self._deadTimeButton[i].setDisabled(True)
                if self.systemController.stimulationProtocol.GetAction() == 2:
                    x0.append(x0[-1])
                    y.append(0)
                x0.extend(np.arange(x0[-1], x0[-1] +self._timeButton[i].value()+1, 1).tolist())
                y.extend([0]*(self._timeButton[i].value()+1))
            else:
                self._frequencyButton[i].setDisabled(False)
                self._deadTimeButton[i].setDisabled(False)
                if self.systemController.stimulationProtocol.GetAction() == 0:
                    for j in range(0,self._timeButton[i].value()*self._frequencyButton[i].value()):
                        x0.append(x0[-1])
                        y.append(1)
                        x0.append(x0[-1]+(1/(2*self._frequencyButton[i].value()))-(self._deadTimeButton[i].value()/1000))
                        y.append(1)
                        x0.append(x0[-1])
                        y.append(0)
                        x0.append(x0[-1]+(self._deadTimeButton[i].value()/1000))
                        y.append(0)
                        x0.append(x0[-1]+(1/(2*self._frequencyButton[i].value()))-(self._deadTimeButton[i].value()/1000))
                        y.append(0)
                        x0.append(x0[-1]+(self._deadTimeButton[i].value()/1000))
                        y.append(0)
                elif self.systemController.stimulationProtocol.GetAction() == 1:
                    for j in range(0,self._timeButton[i].value()*self._frequencyButton[i].value()):
                        x0.append(x0[-1])
                        y.append(1)
                        x0.append(x0[-1]+(1/(2*self._frequencyButton[i].value()))-(self._deadTimeButton[i].value()/1000))
                        y.append(1)
                        x0.append(x0[-1])
                        y.append(0)
                        x0.append(x0[-1]+(self._deadTimeButton[i].value()/1000))
                        y.append(0)
                        x0.append(x0[-1])
                        y.append(-1)
                        x0.append(x0[-1]+(1/(2*self._frequencyButton[i].value()))-(self._deadTimeButton[i].value()/1000))
                        y.append(-1)
                        x0.append(x0[-1])
                        y.append(0)
                        x0.append(x0[-1]+(self._deadTimeButton[i].value()/1000))
                        y.append(0)
                else:
                    x0.append(x0[-1])
                    y.append(1)
                    x0.append(x0[-1]+self._timeButton[i].value())
                    y.append(1)
        return x0, y
    
    ### 更新設定訊號圖表
    def RenewPlot(self, plot):
        plot.clear()
        x0 = self.CalculateTheSignalPlot()[0]
        y = self.CalculateTheSignalPlot()[1]
        plot.plot().setData(x0, y, pen = "b")
        plot.setXRange(0,x0[-1])
        self.systemController.arduinoController.SensorResultDurationData["Signal"] = x0
    

    ### 更新實時訊號圖表
    def RenewSignalPlotInRealtime(self, plotInStimulation, plotInCamera, cameraPlot):
        if self._tab.currentIndex() == 2: 
            plotInCamera.clear()
            x0 = self.CalculateTheSignalPlot()[0]
            y = self.CalculateTheSignalPlot()[1]
            thisIndex = len(list(filter(lambda x: x <= self._increment, x0)))
            if self.systemController.isSignalStopping == True:
                self.systemController.arduinoController.SensorResultValueData["Signal"].extend(len(y[self.lastIndex:thisIndex])*[0])
            else:
                self.systemController.arduinoController.SensorResultValueData["Signal"].extend(y[self.lastIndex:thisIndex])
            self.lastIndex = thisIndex
            plotInCamera.plot().setData(x0[:self.lastIndex], self.systemController.arduinoController.SensorResultValueData["Signal"], pen = "b")
            plotInCamera.setXRange(0,x0[-1])
            cameraPlot.setXRange(0,x0[-1])
        else:
            plotInStimulation.clear()
            x0 = self.CalculateTheSignalPlot()[0]
            y = self.CalculateTheSignalPlot()[1]
            thisIndex = len(list(filter(lambda x: x <= self._increment, x0)))
            if self.systemController.isSignalStopping == True:
                self.systemController.arduinoController.SensorResultValueData["Signal"].extend(len(y[self.lastIndex:thisIndex])*[0])
            else:
                self.systemController.arduinoController.SensorResultValueData["Signal"].extend(y[self.lastIndex:thisIndex])
            self.lastIndex = thisIndex
            plotInStimulation.plot().setData(x0[:self.lastIndex], self.systemController.arduinoController.SensorResultValueData["Signal"], pen = "b")
            plotInStimulation.setXRange(0,x0[-1])

    ### 更新相機圖表
    def RenewContourPlotInRealtime(self):
        if  self._tab.currentIndex() == 2:
            self.contourPlot.plot().setData(self.systemController.videoController.frameThatMouseStayedInTheChamber, self.systemController.videoController.whichAreaMouseStayedDuringStimulation, pen = "b")
    
    ##Purpose : Realtime renew sensor plot.
    def RenewRealtimePlot(self):
        if  self._tab.currentIndex() == 3:
            for key in self._currentOpenSensorCheckbox:
                if self._currentOpenSensorCheckbox[key].isChecked() == True:
                    self._currentOpenSensorRealtimePlot[key].clear()
                    # showing x and y grids
                    xMinRange = 0.0
                    if self._increment < 10:
                        xMinRange = 0
                        self._currentOpenSensorRealtimePlot[key].setXRange(xMinRange, 10, padding=0)
                    else:
                        xMinRange = self._increment-10
                        self._currentOpenSensorRealtimePlot[key].setXRange(xMinRange, self._increment, padding=0)

                    # ploting line in green color
                    if key == "Vibration":
                        self._currentOpenSensorRealtimePlot[key].plot().setData(self.systemController.GetTimelineData(sensorType = "VibrationX"), self.systemController.GetValueData(sensorType = "VibrationX"), pen = "b")
                        self._currentOpenSensorRealtimePlot[key].plot().setData(self.systemController.GetTimelineData(sensorType = "VibrationY"), self.systemController.GetValueData(sensorType = "VibrationY"), pen = "green")
                        self._currentOpenSensorRealtimePlot[key].plot().setData(self.systemController.GetTimelineData(sensorType = "VibrationZ"), self.systemController.GetValueData(sensorType = "VibrationZ"), pen = "maroon")
                        if self.systemController.sensorDetectionProtocol.GetTheVauleOfIsSensorChangeSignal() == True:
                            self._currentOpenSensorRealtimePlot[key].plot().setData([0, self.totalDuration], [self. systemController.sensorDetectionProtocol.GetSensorThresholdData(sensorType = "Vibration"),  self. systemController.sensorDetectionProtocol.GetSensorThresholdData(sensorType = "Vibration")], pen = "r")
                        
                    else:
                        self._currentOpenSensorRealtimePlot[key].plot().setData(self.systemController.GetTimelineData(sensorType = key), self.systemController.GetValueData(sensorType = key), pen = "b")
                        if self.systemController.sensorDetectionProtocol.GetTheVauleOfIsSensorChangeSignal() == True:
                            self._currentOpenSensorRealtimePlot[key].plot().setData([0, self.totalDuration], [self. systemController.sensorDetectionProtocol.GetSensorThresholdData(sensorType = key), self. systemController.sensorDetectionProtocol.GetSensorThresholdData(sensorType = key)], pen ='r')
                        
    ### 將表格變為空白表格
    def RenewProtocolTableToBlank(self):
        self._rowHeader.clear()
        self._functionButton.clear()
        self._timeButton.clear()
        self._frequencyButton.clear()
        self._deadTimeButton.clear()
        self._actionButton[0].setChecked(True)
        self.systemController.stimulationProtocol.RenewToDefaultData()
        self._protocolTable.setColumnCount(0)
        self._protocolTable.setVerticalHeaderLabels(self._columnHeader)

        for i in range(0, len(self.systemController.stimulationProtocol.GetStepData())):
            self.AddRightColumnInProtocolTable(index=i)
        
        self.RenewPlot(self._plot)


    ### 將表格清空，數量歸零
    def ClearAllProtocolTable(self):
        self._rowHeader.clear()
        self._functionButton.clear()
        self._timeButton.clear()
        self._frequencyButton.clear()
        self._deadTimeButton.clear()
        self._protocolTable.setColumnCount(0)
        self._protocolTable.setVerticalHeaderLabels(self._columnHeader)
    
    ### 改變相機偵測型態
    def ChangeContourDetectType(self, dropdown):
        self.systemController.videoController.ChangeContourDetect(dropdown.currentText())
        if self.systemController.videoController.GetCurrentContextString == "Pause":
            self.mediaStopButton.setText("Stop Detection System")
            self.mediaStopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
    
    ### 改變相機偵測行為型態
    def ChangeBehaviorType(self, dropdown):
        self.systemController.videoController.ChangeBehaviorTest(dropdown.currentText())
        self.contourDetectTypeDropdown.clear()
        if self.systemController.videoController.GetCurrentBehaviorString() == "Light Dark Box":
            self.contourDetectTypeDropdown.addItems(self._lightDarkBoxTriggerType)
            self.rightContourPixelsLabel.setVisible(False)
            self.rightSuggestedContourThresholdTitle.setVisible(False)
            self.rightContourThresholdInputField.setVisible(False)
            self.contourPixelsLabel.setText("Pixels Number: 0")
            self.areaStayDurationText.setText("Duration(Inside/outside ROI):" + str(self.systemController.videoController.GetLeftAreaStayDuration()) + "/" + str(self.systemController.videoController.GetRightAreaStayDuration()))
        else:
            self.contourDetectTypeDropdown.addItems(self._placePreferenceTriggerType)
            self.rightContourPixelsLabel.setVisible(True)
            self.rightSuggestedContourThresholdTitle.setVisible(True)
            self.rightContourThresholdInputField.setVisible(True)
            self.contourPixelsLabel.setText("Left Pixels Number: 0")
            self.areaStayDurationText.setText("Duration(L/M/R):" + str(self.systemController.videoController.GetLeftAreaStayDuration())+ "/" + str(self.systemController.videoController.GetMiddleAreaStayDuration())+ "/" + str(self.systemController.videoController.GetRightAreaStayDuration()))
    
    ### 改變相機偵測顏色
    def ChangeContourThresholdColor(self, dropdown):
        if dropdown.currentText()== "White Background, Black Mice":
            self.systemController.videoController.SetContourDetectColor(255)
        else:
            self.systemController.videoController.SetContourDetectColor(0)

    ### 停止相機
    def StopVideo(self):
        if self.systemController.videoController.GetCurrentContextString() == "Pre-Detect":
            self.systemController.videoController.SetCurrentContextString("Calculate")

        if self.systemController.videoController.GetCurrentContextString() == "Calculate":
            self.systemController.videoController.isResultVideoRecording = False
            self.mediaStopButton.setText("Stop Detection System")
        else:    
            self.systemController.videoController.SetCurrentContextString("Stop")
            self.mediaStopButton.setText("Restart Detection System")

    ### 停止系統
    def StopSystem(self):
        self._timer.stop()
        self._realtimePlotTimer.stop()
        self._timer.timeout.disconnect(self.RepeatStimulation)
        self.stopButton.setDisabled(True)
        self.progressbar.setValue(0)
        self.systemController.arduinoController.OutputTextToArduino("AllStop")
        self.systemController.videoController.SetCurrentContextString("Stop")
        self.systemController.SaveCameraResultsToCsvFile()
        self.systemController.SaveStimulationResultsToCsvFile()
        self.systemController.arduinoController.ClearAllRealtimeData()
        self.systemController.videoController.ClearCameraData()

        self.AbleStimulationPage()
        self._increment = 0
        self.totalDuration = 0
        self.lastIndex = 0

    ### 開始系統
    def StartSystem(self):
        self.systemController.OutputStimulationSettingToArduino()
        self.systemController._eventSignal.clear()
        sensorOpenData = self.systemController.sensorDetectionProtocol.GetAllSensorOpenData()
        for key in sensorOpenData:
            if sensorOpenData[key] == True:
                self._currentOpenSensorCheckbox[key] = self._sensorCheckbox[key]
                self._currentOpenSensorRealtimePlot[key] = self._sensorRealtimePlot[key]
        self._timer.timeout.connect(self.RepeatStimulation)
        self._realtimePlotTimer.timeout.connect(self.RenewRealtimePlot)
        self._realtimePlotTimer.timeout.connect(lambda: self.RenewSignalPlotInRealtime(self.realSignalPlot, self.realSignalPlotInCameraPage, self.contourPlot))
        self._realtimePlotTimer.timeout.connect(self.RenewContourPlotInRealtime)
        self._timer.start(1000)
        self._realtimePlotTimer.start(30)
        self.stopButton.setDisabled(False)
        self.DisableStimulationPage()
        self.systemController.stimulationProtocol.SetTotalDuration(0)
        self.systemController.SaveLastestParametersToCsvFile()
        self.systemController.videoController.ClearTheStimulationResultData()
        self._increment = 0
        self._currentStep = 0
        self._currentDuration = 0
        self._currentDuration += self.systemController.stimulationProtocol.GetDurationData()[0][self._currentStep]

        for i in range(0, len(self.systemController.stimulationProtocol.GetDurationData()[0])):
            self.totalDuration += self.systemController.stimulationProtocol.GetDurationData()[0][i]
        
        self.systemController.stimulationProtocol.totalDuration = self.totalDuration
        self.systemController.StartSystemTimeCounting()
        self.systemController.videoController._currentContextString = "Detect"
        self.systemController.videoController.isResultVideoRecording = False
            
    ### 重複刺激
    def RepeatStimulation(self):
        if self._increment == self._currentDuration:
            self._currentStep += 1
            if self._increment < self.totalDuration:
                self._currentDuration += self.systemController.stimulationProtocol.GetDurationData()[0][self._currentStep]
        if self._increment >= self.totalDuration:
            self.SetStopMessage("The Stimulation is over.")
            self.StopSystem()
        else:
            self._increment += 1
            self.progressbar.setValue(int(self._increment/self.totalDuration*100))

        if self.systemController.videoController._currentContextString == "Detect":
            self.areaStayDurationText.setText(self.systemController.videoController.GetMouseStayDurationRatio())
            if self.systemController.videoController.GetStimulationStateWithMicePosition() == True:
                self.stimulationStateLabel.setText("Mice is in the "+ self.systemController.videoController._miceCurrentPosition +" chamber. Stimulation On.")
            else:
                self.stimulationStateLabel.setText("Mice is in the "+ self.systemController.videoController._miceCurrentPosition +" chamber. Stimulation Off.")

    ### 選擇Arduino埠
    def ChooseArduinoPort(self):
        ports = self.systemController.arduinoController.GetCurrentPortsAvailable()
        comPort = self.systemController.arduinoController.GetComPort()

        if comPort != "COM" and comPort != "":
            text, ok = QtWidgets.QInputDialog().getItem(QWidget(), '', "Current Arduino Port:" + comPort +'\nSet the Port Number of Arduino.', ports, 0)
        else:
            text, ok = QtWidgets.QInputDialog().getItem(QWidget(), '', "Current Arduino Port: None" +'\nSet the Port Number of Arduino.', ports, 0)

        self.SetStopMessage(self.systemController.arduinoController.SetComPortAndSearchArduino(text = text))

    ### 開啟相機頁面
    def AbleCameraPage(self):
        self.mediaStopButton.setEnabled(False)
        self.playVideoButton.setEnabled(True)
        self.clearPointButton.setEnabled(True)
        self.contourDetectTypeDropdown.setEnabled(True)
        self.leftContourColorDropdown.setEnabled(True)
        self.leftContourThresholdInputField.setEnabled(True)
        self.rightContourThresholdInputField.setEnabled(True)
        self._loadButton.setEnabled(True)
        self.behaviorTypeDropDown.setEnabled(True)

    ### 設定相機頁面為偵測模式
    def SetCameraPageDetectMode(self):
        self.mediaStopButton.setEnabled(True)
        self.playVideoButton.setEnabled(False)
        self.clearPointButton.setEnabled(True)
        self.contourDetectTypeDropdown.setEnabled(True)
        self.leftContourColorDropdown.setEnabled(True)
        self.leftContourThresholdInputField.setEnabled(True)
        self.rightContourThresholdInputField.setEnabled(True)
        self._loadButton.setEnabled(False)
        self.behaviorTypeDropDown.setEnabled(True)
    
    ### 關閉相機頁面
    def DisableCameraPage(self):
        self.mediaStopButton.setEnabled(False)
        self.playVideoButton.setEnabled(False)
        self.clearPointButton.setEnabled(False)
        self.contourDetectTypeDropdown.setEnabled(False)
        self.leftContourColorDropdown.setEnabled(False)
        self.leftContourThresholdInputField.setEnabled(False)
        self.rightContourThresholdInputField.setEnabled(False)
        self._loadButton.setEnabled(False)
        self.behaviorTypeDropDown.setEnabled(False)

    ### 展示畫面
    def ShowFrame(self, revertColorFrame, width, height, bytesPerline):
        self.qFrameImage = QImage(revertColorFrame, width, height, bytesPerline, QImage.Format_RGB888)
        self.frameLabel.setPixmap(QPixmap.fromImage(self.qFrameImage))

    ### 依照上次刺激參數調整UI
    def SetUIWithLastestParameters(self):
        self._actionButton[self.systemController.stimulationProtocol._actionIndex].setChecked(True)
        if self.systemController.sensorDetectionProtocol._isSensorChangeSignal == True:
            self.sensorChangeSignalDropDown.setCurrentIndex(1)
        else:
            self.sensorChangeSignalDropDown.setCurrentIndex(0)
        self.sensorChangeSignalDropDown.currentIndexChanged.connect(lambda: self.systemController.sensorDetectionProtocol.ReverseTheVauleOfIsSensorChangeSignal())

        self.magneticFieldDetectionCheckBox.setChecked(self.systemController.sensorDetectionProtocol._isSensorOpenData['MagneticField'])
        self.temperatureDetectionCheckBox.setChecked(self.systemController.sensorDetectionProtocol._isSensorOpenData['Temperature'])
        self.soundDetectionCheckBox.setChecked(self.systemController.sensorDetectionProtocol._isSensorOpenData['Sound'])
        self.vibrationDetectionCheckBox.setChecked( self.systemController.sensorDetectionProtocol._isSensorOpenData['Vibration'])

        self.magneticFieldThresholdInputField.setText(str(self.systemController.sensorDetectionProtocol._sensorThresholdData['MagneticField']))
        self.temperatureThresholdInputField.setText(str(self.systemController.sensorDetectionProtocol._sensorThresholdData['Temperature']))
        self.vibrationThresholdInputField.setText(str(self.systemController.sensorDetectionProtocol._sensorThresholdData['Vibration']))
        self.soundThresholdInputField.setText(str(self.systemController.sensorDetectionProtocol._sensorThresholdData['Sound']))

        if self.systemController.videoController._miceDetectColor == 255:
            self.leftContourColorDropdown.setCurrentIndex(0)
        else:
            self.leftContourColorDropdown.setCurrentIndex(1)
        self.leftContourColorDropdown.currentIndexChanged.connect(lambda: self.ChangeContourThresholdColor(dropdown=self.leftContourColorDropdown))

        if self.systemController.videoController._currentBehaviorString == "Light Dark Box" :
            self.behaviorTypeDropDown.setCurrentIndex(self.systemController.videoController.behaviorString["Light Dark Box"])
        elif self.systemController.videoController._currentBehaviorString == "Place Preference Test":
            self.behaviorTypeDropDown.setCurrentIndex(self.systemController.videoController.behaviorString["Place Preference Test"])
        else:
            self.behaviorTypeDropDown.setCurrentIndex(self.systemController.videoController.behaviorString["Marble Burying Test"])
        
        self.leftContourThresholdInputField.setText(str(self.systemController.videoController._leftContourThreshold))
        self.rightContourThresholdInputField.setText(str(self.systemController.videoController._rightContourThreshold))
    
    def SetCameraUIPreCalculationStatus(self):
        self.clearPointButton.setEnabled(True)
        self.playVideoButton.setEnabled(True)
        self.mediaStopButton.setEnabled(True)
        self.mediaStopButton.setText("Start Calculate")
    
    def RenewInformInCalculationStatus(self, information):
        self.stimulationStateLabel.setText(information)

if __name__ == '__main__': 
    app = QApplication(sys.argv)
    controller = UIController()
    controller.show()
    sys.exit(app.exec_())