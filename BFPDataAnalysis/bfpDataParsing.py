__author__ = 'arosado'
import csv
import os

class BFPData:
    currentDirectory = None
    currentFile = None

    def parseFile(self):
        fileText = self.currentFile.read()
        fileLines = fileText.split('\n')
        expParaLines = fileLines[0:3]
        expLines = fileLines[4:len(fileLines)]
        expPara = {}
        expData = []
        startEvent = True
        startTime = False
        eventData = []
        eventInfo = []
        count = 0
        firstExpParaLine = True
        secondExpParaLine = False
        thirdExpParaLine = False
        for line in expParaLines:
            lineData = line.split('\t')
            if firstExpParaLine:
                expPara['experimentMode'] = float(lineData[0])
                expPara['edgesNumber'] = float(lineData[1])
                expPara['u2ratio'] = float(lineData[2])
                expPara['velocityBias'] = float(lineData[3])
                firstExpParaLine = False
                secondExpParaLine = True
            elif secondExpParaLine:
                expPara['springConstant'] = float(lineData[0])
                expPara['pipetteDiameter'] = float(lineData[1])
                expPara['rbcCellDiameter'] = float(lineData[2])
                expPara['contactDiscDiameter'] = float(lineData[3])
                expPara['beadDiameter'] = float(lineData[4])
                expPara['aspiratedLength'] = float(lineData[5])
                expPara['aspirationPressure'] = float(lineData[6])
                expPara['temperature'] = float(lineData[7])
                expPara['viscosity'] = float(lineData[8])
                expPara['corticalTension'] = float(lineData[9])
                secondExpParaLine = False
                thirdExpParaLine = True
            elif thirdExpParaLine:
                expPara['impingingRate'] = float(lineData[0])
                expPara['loadingRate'] = float(lineData[1])
                expPara['primingRate'] = float(lineData[2])
                expPara['retractingRate'] = float(lineData[3])
                expPara['impingmentForce'] = float(lineData[4])
                expPara['clampForce'] = float(lineData[5])
                expPara['activationForce'] = float(lineData[6])
                expPara['timeoutAtClamp'] = float(lineData[7])
                expPara['contactTimeInSeconds'] = float(lineData[8])
                expPara['cycleInterval'] = float(lineData[9])
                firstExpParaLine = True
                secondExpParaLine = False
                thirdExpParaLine = False
        for line in expLines:
            lineData = line.split('\t')
            if startEvent:
                for data in lineData:
                    eventInfo.append(float(data))
                startEvent = False
                startTime = True
            else:
                if startTime:
                    for data in lineData:
                        eventData.append(float(data))
                else:
                    if (0.000000 == eventInfo[0]) and (0.0000000 == eventInfo[1]):
                        startEvent = True
                        startTime = True
                    for data in lineData:
                        eventData.append(float(data))

    def parseFilesInDirectory(self):
        if self.currentDirectory != None:
            fileList = os.listdir(self.currentDirectory)
            for file in fileList:
                currentPath = os.path.join(self.currentDirectory, file)
                if os.path.isdir(currentPath):
                    pass
                if os.path.isfile(currentPath):
                    self.currentFile = open(currentPath, 'r')
                    self.parseFile()

    def setCurrentFileDirectory(self, dataDirectory):
        if os.path.isdir(dataDirectory):
            self.currentDirectory = dataDirectory

    def __init__(self):
        pass


dataApi = BFPData()
dataApi.setCurrentFileDirectory('../SampleData')
dataApi.parseFilesInDirectory()