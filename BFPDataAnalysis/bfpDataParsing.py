__author__ = 'arosado'
import os
import matplotlib.pyplot as plt
import numpy as np

class BFPData:
    currentDirectory = None
    currentFile = None

    def parseFile(self):
        fileText = self.currentFile.read()
        fileLines = fileText.split('\n')
        expParaLines = fileLines[0:3]
        expLines = fileLines[4:len(fileLines)]
        expPara = {}
        startData = True
        startTime = False
        expData  = {}
        count = 0
        firstExpParaLine = True
        secondExpParaLine = False
        thirdExpParaLine = False
        allFileData = []
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
            if startData:
                eventNumber = float(lineData[2])
                startTime = True
                startData = False
                data = []
            else:
                if (0.000000 == float(lineData[0])) and (0.000000 == float(lineData[1])) and (0.000000 == float(lineData[3])):
                    eventNumber = float(lineData[2])
                    startData = True
                    startTime = True
                    expData['data'] = data
                    expData['eventNumber'] = eventNumber
                    allFileData.append(expData)
                    self.analyzeExperimentalData(expPara, data)
                    expData = {}
                    data = []
                else:
                    timeStamp = float(lineData[0])
                    bfpState = float(lineData[1])
                    piezoVoltage = float(lineData[2])
                    peakPosition = float(lineData[3])
                    dataLine = {'timeStamp': timeStamp,
                                'bfpState': bfpState,
                                'piezoVoltage': piezoVoltage,
                                'peakPosition': peakPosition}
                    data.append(dataLine)

    def determineZeroForcePixelPosition(self, zeroStateArray):
        zeroForcePP = np.mean(zeroStateArray)
        return zeroForcePP

    def convertToForce(self, peakPositionArray, zeroForcePP, expPara):
        springConstnat = expPara['springConstant']
        differenceFromZero = np.array(peakPositionArray) - zeroForcePP
        timesSpringConstant = differenceFromZero * springConstnat
        return timesSpringConstant

    def analyzeExperimentalData(self, expPara, dataArray):
        time = []
        peakLocation = []
        bfpState = []
        zeroState = []
        zeroStateTime = []
        oneState = []
        oneStateTime = []
        twoState = []
        twoStateTime = []
        threeState = []
        threeStateTime = []
        fourState = []
        fourStateTime = []
        fiveState = []
        fiveStateTime = []

        for data in dataArray:
            time.append(data['timeStamp'])
            peakLocation.append(data['peakPosition'])
            bfpState.append(data['bfpState'])
            if data['bfpState'] == 0.0:
                zeroState.append(data['peakPosition'])
                zeroStateTime.append(data['timeStamp'])
            if data['bfpState'] == 1.0:
                oneState.append(data['peakPosition'])
                oneStateTime.append(data['timeStamp'])
            if data['bfpState'] == 2.0:
                twoState.append(data['peakPosition'])
                twoStateTime.append(data['timeStamp'])
            if data['bfpState'] == 3.0:
                threeState.append(data['peakPosition'])
                threeStateTime.append(data['timeStamp'])
            if data['bfpState'] == 4.0:
                fourState.append(data['peakPosition'])
                fourStateTime.append(data['timeStamp'])
            if data['bfpState'] == 5.0:
                fiveState.append(data['peakPosition'])
                fiveStateTime.append(data['timeStamp'])

        zeroPeakPosition = self.determineZeroForcePixelPosition(zeroState)
        forceArray = self.convertToForce(peakLocation, zeroPeakPosition, expPara)
        zeroStateForceArray = self.convertToForce(zeroState, zeroPeakPosition, expPara)
        oneStateForceArray = self.convertToForce(oneState, zeroPeakPosition, expPara)
        twoStateForceArray = self.convertToForce(twoState, zeroPeakPosition, expPara)
        threeStateForceArray = self.convertToForce(threeState, zeroPeakPosition, expPara)
        fourStateForceArray = self.convertToForce(fourState, zeroPeakPosition, expPara)
        fiveStateForceArray = self.convertToForce(fiveState, zeroPeakPosition, expPara)

        plt.figure(1)
        plt.plot(zeroStateTime, zeroStateForceArray)
        plt.plot(oneStateTime, oneStateForceArray)
        plt.plot(twoStateTime, twoStateForceArray)
        plt.plot(threeStateTime, threeStateForceArray)
        plt.plot(fourStateTime, fourStateForceArray)
        plt.plot(fiveStateTime, fiveStateForceArray)
        plt.ylabel('Force')
        plt.xlabel('Time')

        plt.figure(2)
        plt.plot(time, bfpState)
        plt.ylabel('BFP State')
        plt.xlabel('Time')



        plt.show()

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