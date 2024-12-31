import cv2
from datetime import datetime
import numpy as np

class VideoController:
    contextString = {"Not Connected": 0 ,"BeforePlay": 1, "ScreenShot": 2, "SelectROI": 3, "Pre-Detect": 4, "Detect": 5, "Playing": 6, "Pause": 7, "Stop": 8, "End": 9}
    behaviorString = {"Light Dark Box" : 0, "Place Preference Test" : 1}

    _systemController = None
    _currentContextString = ""
    _currentBehaviorString = ""
    currentAreaTriggerType = ""
    loadingVideoFileName = ""
    _streamVideoFileName = ""
    _miceCurrentPosition = ""

    _isCameraChangeSignal = False
    _miceDetectColor = 0
    _leftContourThreshold = 20000
    _rightContourThreshold = 20000
    _colorThreshold = 127
    _isDetectingContourRange = False
    _leftAreaStayFrame = 0
    _middleAreaStayFrame = 0
    _rightAreaStayFrame = 0
    time = 0

    _pointsOfArea = []
    _leftArea = []
    _rightArea = []

    whichAreaMouseStayedDuringStimulation = []
    frameThatMouseStayedInTheChamber = []

    frame = None
    _result = None
    _resultName = ""
    _status = ""

    leftPixels = 0
    rightPixels = 0
    suggestedMinimumContourPixel = 0
    suggestedMaximumContourPixel = 0 

    rightSuggestedMinimumContourPixel = 0
    rightSuggestedMaximumContourPixel = 0

    isVideoPlaying = True
    isResultVideoRecording = True

    def SetSystemController(self, controller):
        self._systemController = controller
    
    def SetCurrentAreaTriggerType(self, value: str):
        self.currentAreaTriggerType = value

    def GetCurrentAreaTriggerType(self):
        return self.currentAreaTriggerType

    def SetCurrentContextString(self, value: str):
        self._currentContextString = value

    def GetCurrentContextString(self):
        return self._currentContextString

    def GetCurrentBehaviorString(self):
        return self._currentBehaviorString
    
    def SetLeftContourThreshold(self, value: int):
        self._leftContourThreshold = value
    
    def GetLeftContourThreshold(self):
        return self._leftContourThreshold

    def SetRightContourThreshold(self, value: int):
        self._rightContourThreshold = value

    def GetRightContourThreshold(self):
        return self._rightContourThreshold

    def GetLeftAreaStayDuration(self):
        return self._leftAreaStayFrame
    
    def GetMiddleAreaStayDuration(self):
        return self._middleAreaStayFrame

    def GetRightAreaStayDuration(self):
        return self._rightAreaStayFrame

    def GetWhichAreaMouseStayedDuringStimulation(self):
        return self.whichAreaMouseStayedDuringStimulation
    
    def GetFrameThatMouseStayedInTheChamber(self):
        return self.frameThatMouseStayedInTheChamber

    def SetContext(self, state: str):
        self._currentContextString = state

    def SetContourDetectColor(self, value):
        self._miceDetectColor = value
    
    def GetContourDetectColor(self):
        return self._miceDetectColor 

    def ReverseTheVauleOfIsCameraChangeSignal(self, value: bool):
        self._isCameraChangeSignal = value
    
    def GetTheVauleOfIsCameraChangeSignal(self):
        return self._isCameraChangeSignal
    
    def GetVideoDuration(self, cap):
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            videoDuration = frame_count / fps
            self._systemController.uiController.totalDuration = videoDuration
            return frame_count, videoDuration

    def Request(self):
        self.state.Handle()

    def ChangeContourDetect(self, value):
        self.currentAreaTriggerType = value
        if self._currentContextString == "Pause":
            self._currentContextString = "BeforePlay"

    def ChangeBehaviorTest(self, value):
        self._currentBehaviorString = value
        if self._currentContextString == "Pause":
            self._currentContextString = "BeforePlay"
    

    ### 確認是否具有影像
    def CheckIfVideoIsAbled(self):
        cap = self.LoadVideo()
        if cap.isOpened() == False:
            self._systemController.uiController.SetStopMessage("There is no video or stream.")
        else:
            if self._systemController.isCameraReadingStarted == False:
                self._systemController.SetCameraReadingStarted()
                self._currentContextString = "BeforePlay"
            else:
                self._systemController.uiController.SetStopMessage("Already Start.")
                if self._status == "Video":
                    self._currentContextString = "Calculation"
        

    ### 讀取影像
    def LoadVideo(self):
        if self.loadingVideoFileName != "" :
            cap = cv2.VideoCapture(self.loadingVideoFileName)
            self._status = "Video"
        else:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self._status = "Camera"

        return cap

    ### 重設偵測區域
    def ResetDetectArea(self):
        self._pointsOfArea.clear()
        self._leftArea.clear()
        self._rightArea.clear()
        self._currentContextString = "ScreenShot"

    ### 清除刺激結果資料
    def ClearTheStimulationResultData(self):
        self.whichAreaMouseStayedDuringStimulation.clear()
        self.frameThatMouseStayedInTheChamber.clear()

    ### 計算小鼠在每個區域的時間
    def CalculateTheDurationThatMiceStayedInEachArea(self, totalDuration):
        totalMiceStayedFrame = self._leftAreaStayFrame + self._middleAreaStayFrame + self._rightAreaStayFrame
        if totalMiceStayedFrame != 0:
            leftChamberStayedDuration = self._leftAreaStayFrame/totalMiceStayedFrame*totalDuration
            middleChamberStayedDuration = self._middleAreaStayFrame/totalMiceStayedFrame*totalDuration
            rightChamberStayedDuration = self._rightAreaStayFrame/totalMiceStayedFrame*totalDuration
        else:
            leftChamberStayedDuration = 0
            middleChamberStayedDuration = 0
            rightChamberStayedDuration = 0

        return leftChamberStayedDuration, middleChamberStayedDuration, rightChamberStayedDuration
    
    ### 停止前個影像錄影，並開始新的影像錄影
    def StopPreviousSavingAndStartSavingAnotherVideo(self, cwd, isSavingAnotherVideo, fileName = ""):
        if self._result != None:
            self._result.release()
            self.ChangeVideoFPS(self._resultName)
        
        if isSavingAnotherVideo == True:
            if self._streamVideoFileName == "":
                self._streamVideoFileName = datetime.now().strftime("%Y%m%d_%H%M%S_")
            self._result = cv2.VideoWriter(cwd+"/"+ self._streamVideoFileName + fileName +".mp4",  cv2.VideoWriter_fourcc(*'mp4v'), 10, (960, 640))
            self._resultName = cwd+"/"+ self._streamVideoFileName + fileName +".mp4"
        else:
            self._result = None
            self._resultName = ""


    ### 調整左側區域建議數值範圍
    def DetectLeftContourPixelRange(self):
        if self.suggestedMaximumContourPixel == 0:
            self.suggestedMaximumContourPixel = self.leftPixels
            self.suggestedMinimumContourPixel = self.leftPixels
        else:
            if self.leftPixels < self.suggestedMinimumContourPixel:
                self.suggestedMinimumContourPixel = self.leftPixels
            elif self.leftPixels > self.suggestedMaximumContourPixel:
                self.suggestedMaximumContourPixel = self.leftPixels
        return "Left Contour Threshold: Suggested Range in" + str(self.suggestedMinimumContourPixel) + "-" + str(self.suggestedMaximumContourPixel)
    

    ### 調整右側區域建議數值範圍
    def DetectRighttContourPixelRange(self):
        if self.rightSuggestedMaximumContourPixel == 0:
            self.rightSuggestedMaximumContourPixel = self.rightPixels
            self.rightSuggestedMinimumContourPixel = self.rightPixels
        else:
            if self.rightPixels < self.rightSuggestedMinimumContourPixel:
                self.rightSuggestedMinimumContourPixel = self.rightPixels
            elif self.rightPixels > self.rightSuggestedMaximumContourPixel:
                self.rightSuggestedMaximumContourPixel = self.rightPixels
        return "Right Contour Threshold: Suggested Range in" + str(self.rightSuggestedMinimumContourPixel) + "-" + str(self.rightSuggestedMaximumContourPixel)

    ### 截圖
    def ScreenShot(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.imwrite("Screenshot.png", self.frame)
            self.img = cv2.imread('Screenshot.png')
            if self._currentBehaviorString == "Place Preference Test":
                cv2.putText(self.img,"Select Left Area",(20, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),1,cv2.LINE_AA)
            else:
                cv2.putText(self.img,"Select Detection Area",(20, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),1,cv2.LINE_AA)
            
            if self._pointsOfArea == []:
                self._currentContextString = "SelectROI"
                cv2.imshow("Crop", self.img)
                cv2.waitKey(1)
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.isVideoPlaying = False

    ### 框選偵測區域
    def SelectRegionOfInterest(self, event, x, y, flags,params):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self._pointsOfArea) >= 4:
                self._pointsOfArea.append((x, y))
                self._rightArea.append((x, y))
            else:
                self._pointsOfArea.append((x, y))
                self._leftArea.append((x, y))  
        if event == cv2.EVENT_MBUTTONDOWN:
            if len(self._pointsOfArea) == 4:
                self._rightArea.pop()
                self._pointsOfArea.pop()
                self._pointsOfArea.extend(self._leftArea)
            else:  
                self._leftArea.pop()
                self._pointsOfArea.pop()
        if event == cv2.EVENT_RBUTTONDOWN:
            self.isVideoPlaying = False

        if self._currentBehaviorString == "Place Preference Test":
            cv2.putText(self.img,"Select Left Area",(20, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),1,cv2.LINE_AA)
            if len(self._leftArea) == 4:
                self.img = cv2.imread('screenshot.png')
                self.DrawAreaWithCurrentPoints(image= self.img, area = self._leftArea)
                cv2.putText(self.img,"Select Right Area",(20, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),1,cv2.LINE_AA)
                if len(self._rightArea) == 4:
                    self.DrawAreaWithCurrentPoints(image= self.img, area = self._rightArea)
                    leftBackground = self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._leftArea)[3]
                    rightBackground = self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._rightArea)[3]

                    ### Check if background is same color with mice. 
                    if leftBackground <= 0 or rightBackground <= 0 :
                        self._leftArea.clear()
                        self._rightArea.clear()
                        self._currentContextString = "ScreenShot" 
                        cv2.destroyAllWindows()
                    else:
                        cv2.imshow("gray", self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._leftArea)[0])
                        cv2.imshow("areaROI", self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._leftArea)[1])
                        cv2.moveWindow("areaROI", 500, 600)
                        self._currentContextString = "Pre-Detect"
                        cv2.destroyAllWindows()
                        cv2.waitKey(1)
                        self.isVideoPlaying = True
                else:
                    self.DrawAreaWithCurrentPoints(image= self.img, area = self._rightArea)
            else:
                self.DrawAreaWithCurrentPoints(image= self.img, area = self._leftArea)
        else:
            cv2.putText(self.img,"Select Detection Area",(20, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),1,cv2.LINE_AA)
            if len(self._leftArea) == 4:
                cv2.line(self.img, pt1=self._leftArea[0], pt2=self._leftArea[-1], color=(255, 0, 0), thickness=2)
                leftBackground = self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._leftArea)[3]
                if leftBackground <= 0: 
                    self._leftArea.clear()
                    self._currentContextString = "ScreenShot"
                    cv2.destroyAllWindows()
                else:
                    cv2.imshow("gray", self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._leftArea)[0])
                    cv2.imshow("areaROI", self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._leftArea)[1])
                    cv2.moveWindow("areaROI", 500, 600)
                    self._currentContextString = "Pre-Detect"
                    cv2.destroyAllWindows()
                    cv2.waitKey(1)
                    self.isVideoPlaying = True
            else:
                self.DrawAreaWithCurrentPoints(image= self.img, area = self._leftArea)

        cv2.imshow("Crop", self.img)
    

    ### 標示當前偵測區域
    def DrawAreaWithCurrentPoints(self, image, area):
        if len(area) > 0:
            # Draw The Points of The area
            cv2.circle(image, area[-1], 3, (0, 0, 255), -1)

        if len(area) > 1:
            # Draw The Lines of The area
            for i in range(len(area) - 1):
                cv2.circle(image,area[i], 5, (0, 0, 255), -1)
                cv2.line(image, pt1=area[i], pt2=area[i + 1], color=(255, 0, 0), thickness=2)
        if len(area) == 4:
            cv2.circle(image,area[-1], 5, (0, 0, 255), -1)
            cv2.line(image, pt1=area[0], pt2=area[-1], color=(255, 0, 0), thickness=2)

    
    def SetWholeArea(self, image, leftArea, rightArea):
        for i in range(len(leftArea)-1):
            cv2.circle(image, leftArea[i], 5, (0, 0, 255), -1)  # x ,y 爲鼠標點擊地方的座標
            cv2.line(image, pt1=leftArea[i], pt2=leftArea[i + 1], color=(255, 0, 0), thickness=2)
        cv2.line(image, pt1=leftArea[0], pt2=leftArea[-1], color=(255, 0, 0), thickness=2)


        if self._currentBehaviorString == "Place Preference Test":
            for i in range(len(rightArea)-1):
                cv2.circle(image, rightArea[i], 5, (0, 255, 0), -1)  # x ,y 爲鼠標點擊地方的座標
                cv2.line(image, pt1=rightArea[i], pt2=rightArea[i + 1], color=(0, 0, 255), thickness=2)
            cv2.line(image, pt1=rightArea[0], pt2=rightArea[-1], color=(0, 0, 255), thickness=2) 


    ### 計算並取得該區域的Pixels數值
    def CalculateAndGetTheContourPixelsInTheArea(self, regionOfInterest):
        areaMask = np.zeros(self.frame.shape, np.uint8)
        points = np.array(regionOfInterest, np.int32)
        points = points.reshape((-1, 1, 2))
        # 畫多邊形
        frame = self.frame.copy()
        areaMask = cv2.polylines(frame, [points], isClosed= True, color=(255, 255, 255), thickness=1)
        areaMask2 = cv2.fillPoly(areaMask.copy(), [points], (255, 255, 255))  # 用於求 ROI
        areaROI = cv2.bitwise_xor(frame, areaMask2)
        gray = cv2.cvtColor(areaROI, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        ret, gray = cv2.threshold(gray, self._colorThreshold, 255, cv2.THRESH_BINARY)
        pixels = np.sum(gray == self._miceDetectColor)
        background = np.sum(gray == abs(255 - self._miceDetectColor))

        return gray, areaROI, pixels, background

    ### 重設偵測區域
    def ResetDetectArea(self):
        self._pointsOfArea.clear()
        self._leftArea.clear()
        self._rightArea.clear()
        self._currentContextString = "ScreenShot"

    ### 計算老鼠停留時間
    def MeasureMouseStayDuration(self, time):
        if self._miceCurrentPosition == "Left":
            self._leftAreaStayFrame += 1
            self.frameThatMouseStayedInTheChamber.append(time)
            self.whichAreaMouseStayedDuringStimulation.append(1)
        elif self._miceCurrentPosition == "Right":
            self._rightAreaStayFrame += 1
            self.frameThatMouseStayedInTheChamber.append(time)
            self.whichAreaMouseStayedDuringStimulation.append(-1)
        elif self._miceCurrentPosition == "Inside ROI":
            self._rightAreaStayFrame += 1
            self.frameThatMouseStayedInTheChamber.append(time)
            self.whichAreaMouseStayedDuringStimulation.append(-1)
        elif self._miceCurrentPosition == "Outside ROI":
            self._leftAreaStayFrame += 1
            self.frameThatMouseStayedInTheChamber.append(time)
            self.whichAreaMouseStayedDuringStimulation.append(1)
        else:
            self._middleAreaStayFrame += 1
            self.frameThatMouseStayedInTheChamber.append(time)
            self.whichAreaMouseStayedDuringStimulation.append(0)
    ### 計算老鼠停留時間比率
    def GetMouseStayDurationRatio(self):
        if self._currentBehaviorString == "Light Dark Box":
            return "Duration(L/D, frame):" + str(self._leftAreaStayFrame) + "/" + str(self._rightAreaStayFrame)
        else:
            return "Duration(L/M/R, frame):" + str(self._leftAreaStayFrame)+ "/" + str(self._middleAreaStayFrame) + "/" + str(self._rightAreaStayFrame)

    ### 相機功能循環   
    def RepeatVideoCycle(self, cwd):
        while self._systemController.isCameraReadingStarted == True:
            try:
                if self._currentContextString == "BeforePlay":
                    self.ResetDetectArea()
                    cap = self.LoadVideo()
                elif self._currentContextString == "ReselectFile":
                    if self.loadingVideoFileName == "":
                        break
                    else:
                        self.ResetDetectArea()
                        cap = self.LoadVideo()

                while cap.isOpened():
                    if self.isVideoPlaying == True:
                        ret, self.frame = cap.read()
                    if ret:
                        if self._currentContextString == "ScreenShot":
                            cv2.imshow("Current Frame", self.frame)
                            cv2.moveWindow("Current Frame", 1500, 100)
                            cv2.setMouseCallback('Current Frame',  self.ScreenShot)

                        elif self._currentContextString == "SelectROI":
                            cv2.setMouseCallback('Crop',  self.SelectRegionOfInterest)

                        elif self._currentContextString ==  "Pre-Detect":
                            self.SetWholeArea(image= self.frame, leftArea= self._leftArea, rightArea= self._rightArea)
                            self.ShowImageOnCameraTab()
                            self._systemController.uiController.SetCameraPageDetectMode()

                        elif self._currentContextString == "Detect":
                            self.SetWholeArea(image= self.frame, leftArea= self._leftArea, rightArea= self._rightArea)
                            if self.isResultVideoRecording == False:
                                self.StopPreviousSavingAndStartSavingAnotherVideo(cwd= cwd, isSavingAnotherVideo= True, fileName= "Stimulation")
                                self._systemController.uiController.DisableCameraPage()
                                self.isResultVideoRecording = True
                                self._leftAreaStayFrame = 0
                                self._rightAreaStayFrame = 0
                                self._middleAreaStayFrame = 0
                            self.leftPixels = self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._leftArea)[2]
                            self._systemController.uiController.contourPixelsLabel.setText("Left Pixels:" + str(self.leftPixels))
                            if self._currentBehaviorString == "Place Preference Test":
                                self.rightPixels = self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._rightArea)[2]
                                self._systemController.uiController.rightContourPixelsLabel.setText("Right Pixels:" + str(self.rightPixels))
                            self.ShowImageOnCameraTab()
                            if self._isDetectingContourRange == True:
                                self.DetectLeftContourPixelRange()
                                self._systemController.uiController.leftSuggestedContourThresholdTitle.setText("Left Contour Threshold: Suggested Range in" + str(self.suggestedMinimumContourPixel) + "-" + str(self.suggestedMaximumContourPixel))
                                if self._currentBehaviorString == "Place Preference Test":
                                    self.DetectRighttContourPixelRange()
                                    self._systemController.uiController.rightSuggestedContourThresholdTitle.setText("Right Contour Threshold: Suggested Range in" + str(self.rightSuggestedMinimumContourPixel) + "-" + str(self.rightSuggestedMaximumContourPixel))
                            self.GetMicePosition()
                            if self._systemController.isSensorReadingStarted == True:
                                self._systemController.SignalChangeWithCamera()
                            self.time = self._systemController.GetTimeDurationAfterStart()
                            self.MeasureMouseStayDuration(time = self.time)
                            self._result.write(self.frame)

                        elif self._currentContextString == "Calculate":
                            self.SetWholeArea(image= self.frame, leftArea= self._leftArea, rightArea= self._rightArea)
                            if self.isResultVideoRecording == False:
                                self.StopPreviousSavingAndStartSavingAnotherVideo(cwd= cwd, isSavingAnotherVideo= True, fileName= "Stimulation")
                                frame_count, videoTime = self.GetVideoDuration(cap= cap)
                                self._systemController.stimulationProtocol.SetTotalDuration(videoTime)
                                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                                self._systemController.uiController.DisableCameraPage()
                                self.isResultVideoRecording = True
                                self._leftAreaStayFrame = 0
                                self._rightAreaStayFrame = 0
                                self._middleAreaStayFrame = 0
                                self._systemController.startTime = self._systemController.GetTheCurrentTime()
                            self.leftPixels = self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._leftArea)[2]
                            self._systemController.uiController.contourPixelsLabel.setText("Left pixels:" + str(self.leftPixels))
                            if self._currentBehaviorString == "Place Preference Test":
                                self.rightPixels = self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._rightArea)[2]
                                self._systemController.uiController.rightContourPixelsLabel.setText("Right pixels:" + str(self.rightPixels))
                            self.ShowImageOnCameraTab()
                            if self._isDetectingContourRange == True:
                                self.DetectLeftContourPixelRange()
                                self._systemController.uiController.leftSuggestedContourThresholdTitle.setText("Left Contour Threshold: Suggested Range in" + str(self.suggestedMinimumContourPixel) + "-" + str(self.suggestedMaximumContourPixel))
                                if self._currentBehaviorString == "Place Preference Test":
                                    self.DetectRighttContourPixelRange()
                                    self._systemController.uiController.rightSuggestedContourThresholdTitle.setText("Right Contour Threshold: Suggested Range in" + str(self.rightSuggestedMinimumContourPixel) + "-" + str(self.rightSuggestedMaximumContourPixel))
                            self.GetMicePosition()
                            self.time = self._systemController.GetTimeDurationAfterStart()
                            self._systemController.uiController.RenewInformInCalculationStatus(str(frame_count))
                            frame_count = frame_count - 1
                            self.MeasureMouseStayDuration(time = self.time)
                            self._result.write(self.frame)

                        elif self._currentContextString == "Stop":
                            self.StopPreviousSavingAndStartSavingAnotherVideo(cwd= cwd, isSavingAnotherVideo= False)
                            self._systemController.SaveCameraResultsToCsvFile()
                            self._currentContextString = "Pre-Detect"
                        cv2.waitKey(10)
                    else:
                        if self._currentContextString != "Pre-Detect":
                            self.StopPreviousSavingAndStartSavingAnotherVideo(cwd= cwd, isSavingAnotherVideo= False)
                            self._systemController.SaveCameraResultsToCsvFile()
                            self._currentContextString = "Pre-Detect"
                            self._systemController.uiController.RenewInformInCalculationStatus("The calculation is over.")
                            if self._status == "Video":
                                self._currentContextString = "ReselectFile"
                                self.loadingVideoFileName = ""
                                cap.release()
                                break
            except Exception as error:
                print("An error occurred:", type(error).__name__, type(error).__name__, "–", error)


    ### 取得小鼠位置
    def GetMicePosition(self):
        if self._currentBehaviorString == "Place Preference Test":
            ## Purpose : Check if mice is in the left part of the center chamber.
            if self.leftPixels > self._leftContourThreshold:
                self.isMiceInTheLeftPartOfTheCenter = True
                self._miceCurrentPosition = "Middle-Left"
                self.isMiceInTheMiddleChamber = True
            else:
                self.isMiceInTheLeftPartOfTheCenter = False
                self.isMiceInTheMiddleChamber = False

            ## Purpose : Check if mice is in the Right part of the center chamber.
            if self.rightPixels > self._rightContourThreshold:
                self.isMiceInTheRightPartOfTheCenter = True
                self.isMiceInTheMiddleChamber = True
                
                if self.isMiceInTheLeftPartOfTheCenter == True:
                    self._miceCurrentPosition = "Middle"
                else:
                    self._miceCurrentPosition = "Middle-Right"
            else:
                self.isMiceInTheRightPartOfTheCenter = False
                if self.isMiceInTheLeftPartOfTheCenter != True:
                    self.isMiceInTheMiddleChamber = False
                else:
                    self._miceCurrentPosition = "Middle-Left"

            if self.isMiceInTheMiddleChamber == False:
                ## Purpose : Check if mice is in the left chamber.
                if self._miceCurrentPosition == "Middle-Left":
                    self.isMiceInTheLeftChamber = True
                    self.isMiceInTheLeftPartOfTheCenter = False
                    self._miceCurrentPosition = "Left"

                ## Purpose : Check if mice is in the right chamber.
                elif self._miceCurrentPosition == "Middle-Right":
                    self.isMiceInTheRightChamber = True
                    self.isMiceInTheRightPartOfTheCenter = False
                    self._miceCurrentPosition = "Right"
            
        else:
            ## Purpose : Check if mice is in the left chamber.
            if self.leftPixels> self._leftContourThreshold:
                self._miceCurrentPosition = "Inside ROI"
            else:
                self._miceCurrentPosition = "Outside ROI"

    ### 選擇刺激模式
    def GetStimulationStateWithMicePosition(self):
        if self.currentAreaTriggerType == "Stop stimulation while mice in the ROI.":
            if self._miceCurrentPosition == "Inside ROI":
                return False
            else:
                return True
        
        elif self.currentAreaTriggerType == "Start stimulation while mice in the ROI.":
            if self._miceCurrentPosition == "Inside ROI":
                return True
            else:
                return False
        
        elif self.currentAreaTriggerType == "Stop stimulation while mice in the left chamber.":
            if self._miceCurrentPosition == "Left":
                return False
            else:
                return True
        
        elif self.currentAreaTriggerType == "Start stimulation while mice in the left chamber.":
            if self._miceCurrentPosition == "Left":
                return True
            else:
                return False
        
        elif self.currentAreaTriggerType == "Stop stimulation while mice in the right chamber.":
            if self._miceCurrentPosition == "Right":
                return False
            else:
                return True
        
        elif self.currentAreaTriggerType == "Start stimulation while mice in the right chamber.":
            if self._miceCurrentPosition == "Right":
                return True
            else:
                return False

    ### 展示圖像
    def ShowImageOnCameraTab(self):
        self.frame = cv2.resize(self.frame, (960, 640))
        revertColorFrame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        height, width, channel = revertColorFrame.shape
        bytesPerline = channel * width
        self._systemController.uiController.ShowFrame(revertColorFrame = revertColorFrame, width = width, height = height, bytesPerline = bytesPerline)

        self.contourImg = self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest=  self._leftArea)[0]
        self.contourImg = cv2.resize(self.contourImg, (480, 320))
        self.contourImg = cv2.cvtColor(self.contourImg, cv2.COLOR_BGR2RGB)
        height, width, channel = self.contourImg.shape
        bytesPerline = channel * width

        if self._currentBehaviorString == "Place Preference Test":
            self.contourImgRight = self.CalculateAndGetTheContourPixelsInTheArea(regionOfInterest= self._rightArea)[0]
            self.contourImgRight = cv2.resize(self.contourImgRight, (480, 320))
            self.contourImgRight = cv2.cvtColor(self.contourImgRight, cv2.COLOR_BGR2RGB)
            height, width, channel = self.contourImgRight.shape
            bytesPerline = channel * width
    
    def ClearCameraData(self):
        self.whichAreaMouseStayedDuringStimulation = []
        self.frameThatMouseStayedInTheChamber = []

    ### 改變影像每秒幀數
    def ChangeVideoFPS(self, video):
        if self._systemController.uiController.totalDuration != 0:
            cap = cv2.VideoCapture(video) 
            
            # get FPS of input video 
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # define output video and it's FPS
            output_fps = frame_count/self._systemController.uiController.totalDuration
            # define VideoWriter object 
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
            out = cv2.VideoWriter(self._streamVideoFileName+'_rightFPS.mp4', fourcc, output_fps, 
                                (int(cap.get(3)), int(cap.get(4)))) 
            
            # read and write frams for output video 
            while cap.isOpened(): 
                ret, frame = cap.read() 
                if not ret: 
                    break
                
                out.write(frame) 
            
            # release resources 
            cap.release() 
            out.release() 
            cv2.destroyAllWindows()
    
    def SetVideoPreCalculationStatus(self, fileName):
        self.isVideoPlaying = True
        self._currentContextString = "ScreenShot"
        self.loadingVideoFileName = fileName