__author__ = 'arosado'
import os
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as scistats
import pickle
import json
import csv

class BFPData:
    currentDirectory = None
    currentFile = None
    currentFileName = None
    currentFileData = None
    currentCycleData = None
    currentCycleIndex = None
    allData = []

    def parseFile(self):
        fileText = self.currentFile.read()
        fileLines = fileText.split('\n')
        expParaLines = fileLines[0:3]
        expLines = fileLines[4:len(fileLines)]
        expPara = {}
        startData = True
        startTime = False
        expData = {}
        cycleData = {}
        timeStamps = []
        bfpStates = []
        piezoVoltages = []
        peakPositions = []
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
                indexFileInFile = 0
            else:
                if len(lineData) == 4:
                    if (0.000000 == float(lineData[0])) and (0.000000 == float(lineData[1])) and (0.000000 == float(lineData[3])):
                        eventNumber = float(lineData[2])
                        startData = True
                        startTime = True
                        cycleData['timeStamps'] = timeStamps
                        cycleData['bfpStates'] = bfpStates
                        cycleData['piezoVoltages'] = piezoVoltages
                        cycleData['mainPeakPositions'] = peakPositions
                        cycleData['eventNumber'] = eventNumber
                        cycleData['experimentParameters'] = expPara
                        allFileData.append(cycleData)
                        cycleData = {}
                        timeStamps = []
                        bfpStates = []
                        piezoVoltages = []
                        peakPositions = []
                    else:
                        timeStamp = float(lineData[0])
                        timeStamps.append(timeStamp)
                        bfpState = float(lineData[1])
                        bfpStates.append(bfpState)
                        piezoVoltage = float(lineData[2])
                        piezoVoltages.append(piezoVoltage)
                        peakPosition = float(lineData[3])
                        peakPositions.append(peakPosition)
        self.currentFileData = allFileData
        self.allData.append(allFileData)

    def analyzeAllData(self):
        for fileData in self.allData:
            for cycleData in fileData:
                self.analyzeExperimentalData(cycleData)

    def analyzeCycleInCurrentFile(self, cycleIndex):
        self.currentCycleIndex = cycleIndex
        for i in range(0, len(self.currentFileData)):
            if cycleIndex == i:
                self.analyzeExperimentalData(self.currentFileData[i])

    def determineZeroForcePixelPosition(self, zeroPeakPositions):
        zeroForceMean = np.mean(zeroPeakPositions)
        zeroForceStd = np.std(zeroPeakPositions)
        return zeroForceMean, zeroForceStd

    def convertToForce(self, peakPositionArray, zeroForcePP, expPara):
        springConstant = expPara['springConstant']
        differenceFromZero = np.array(peakPositionArray) - zeroForcePP
        timesSpringConstant = differenceFromZero * expPara['u2ratio'] * 1e3 * springConstant
        return timesSpringConstant

    def analyzeExperimentalData(self, cycleData):
        expParameters = cycleData['experimentParameters']
        timeStamps = cycleData['timeStamps']
        bfpStates = cycleData['bfpStates']
        piezoVoltages = cycleData['piezoVoltages']
        mainPeakPositions = cycleData['mainPeakPositions']

        zeroStateTimepoints = []
        zeroStatePositions = []
        oneStateTimepoints = []
        oneStatePositions = []
        twoStateTimepoints = []
        twoStatePositions = []
        threeStateTimepoints = []
        threeStatePositions = []
        fourStateTimepoints = []
        fourStatePositions = []
        fiveStateTimepoints = []
        fiveStatePositions = []

        for i in range(0, len(timeStamps)):
            if bfpStates[i] == 0.000:
                zeroStatePositions.append(mainPeakPositions[i])
                zeroStateTimepoints.append(timeStamps[i])
            if bfpStates[i] == 1.000:
                oneStatePositions.append(mainPeakPositions[i])
                oneStateTimepoints.append(timeStamps[i])
            if bfpStates[i] == 2.000:
                twoStatePositions.append(mainPeakPositions[i])
                twoStateTimepoints.append(timeStamps[i])
            if bfpStates[i] == 3.000:
                threeStatePositions.append(mainPeakPositions[i])
                threeStateTimepoints.append(timeStamps[i])
            if bfpStates[i] == 4.000:
                fourStatePositions.append(mainPeakPositions[i])
                fourStateTimepoints.append(timeStamps[i])
            if bfpStates[i] == 5.000:
                fiveStatePositions.append(mainPeakPositions[i])
                fiveStateTimepoints.append(timeStamps[i])

        # plt.figure(1)
        # plt.plot(zeroStateTimepoints, zeroStatePositions)
        # plt.plot(oneStateTimepoints, oneStatePositions)
        # plt.plot(twoStateTimepoints, twoStatePositions)
        # plt.plot(threeStateTimepoints, threeStatePositions)
        # plt.plot(fourStateTimepoints, fourStatePositions)
        # plt.plot(fiveStateTimepoints, fiveStatePositions)
        # plt.xlabel('Time in Seconds (s)')
        # plt.ylabel('Position of edge in pixels (px)')
        # plt.show()
        #
        # pass
        #
        # zeroStateAverage = np.average(zeroStatePositions)
        # zeroStateStd = np.std(zeroStatePositions)
        #
        # oneStateAverage = np.average(oneStatePositions)
        # oneStateStd = np.std(oneStatePositions)

        test = self.testChangesInState(cycleData, 10)
        #self.movingAverage(cycleData, 10)

        pass

    def testChangesInState(self, cycleData, frameHolderSize):
        expParameters = np.array(cycleData['experimentParameters'])
        timeStamps = np.array(cycleData['timeStamps'])
        bfpStates = np.array(cycleData['bfpStates'])
        piezoVoltages = np.array(cycleData['piezoVoltages'])
        mainPeakPositions = np.array(cycleData['mainPeakPositions'])

        positionHolder = []
        movingAverage = []
        movingStd = []
        movingTime = []
        differenceSignHolder = []
        stateHolder = []
        movingNormality = []

        normalitySwitch = []

        for i in range(0, len(timeStamps)):
            if (i < frameHolderSize):
                stateHolder.append(0)
            else:
                positionsOfInterest = mainPeakPositions[i-frameHolderSize:i]
                # normalTest = scistats.normaltest(positionsOfInterest)
                average = np.mean(positionsOfInterest)
                std = np.std(positionsOfInterest)

                movingTime.append(timeStamps[i])
                movingStd.append(std)
                movingAverage.append(average)

                #maxStd = np.amax(movingStd)

                averageDifference = mainPeakPositions[i] - average
                averageDifferenceAbs = np.absolute(averageDifference)

                if len(movingStd) > frameHolderSize:
                    stdOfInterest = movingStd[i-frameHolderSize:i]
                    maxStd = np.amax(stdOfInterest)
                else:
                    maxStd = np.amax(movingStd)

                if (maxStd*4 < averageDifferenceAbs):
                    stateHolder.append(1)
                else:
                    stateHolder.append(0)
                # movingNormality.append(normalTest.statistic)


        plt.figure(1)
        plt.plot(timeStamps, mainPeakPositions)

        plt.figure(6)
        plt.plot(timeStamps, stateHolder)
        plt.title('BFP State vs Time')
        plt.xlabel('Time in Seconds (s)')
        plt.ylabel('State')

        plt.figure(2)
        plt.plot(movingTime, movingAverage)
        plt.title('Average over 50 Position Frames')
        plt.xlabel('Time in seconds (s)')
        plt.ylabel('Average position pixel (px)')

        plt.figure(3)
        plt.plot(movingTime, movingStd)
        plt.title('Standard Deviation over 50 Position Frames')
        plt.xlabel('Time in seconds (s)')
        plt.ylabel('Position standard deviation (sigma)')

        plt.figure(4)
        plt.plot(timeStamps, mainPeakPositions)
        plt.title('Peak Positions vs Time')
        plt.xlabel('Time in seconds (s)')
        plt.ylabel('Position in pixels (px)')

        plt.figure(5)
        plt.plot(timeStamps, bfpStates)
        plt.title('BFP State vs Time')
        plt.xlabel('Time in seconds (s)')
        plt.ylabel('BFP State')

        # plt.figure(6)
        # plt.plot(movingTime, movingNormality)
        # plt.title('Moving Normality Statistic 50 Frames')
        # plt.xlabel('Moving Time in Seconds (s)')
        # plt.ylabel('Normality Statistic (Kurtosis and Skew)')

        plt.show()
        pass
        # for i in range(0, len(timeStamps)):
        #     if (i < frameHolderSize):
        #         positionHolder.append(mainPeakPositions[i])
        #         stateHolder.append(0)
        #         pastMovingMin = np.amin(positionHolder)
        #         pastMovingMax = np.amax(positionHolder)
        #     else:
        #         movingAverage.append(np.average(positionHolder))
        #         movingStd.append(np.std(positionHolder))
        #         movingTime.append(timeStamps[i])
        #
        #         #movingNormality.append(scistats.normaltest(positionHolder).pvalue)
        #
        #         currentMovingMax = np.amax(positionHolder)
        #         currentMovingMin = np.amin(positionHolder)
        #
        #         if currentMovingMax > pastMovingMax:
        #             pastMovingMax = currentMovingMax
        #         if currentMovingMin < pastMovingMin:
        #             pastMovingMin = currentMovingMin
        #         bottomHalf = positionHolder[0:int(len(positionHolder)/2)]
        #         topHalf = positionHolder[int(len(positionHolder)/2):len(positionHolder)]
        #         bottomAverage = np.average(bottomHalf)
        #         topAverage = np.average(topHalf)
        #         wholeAverage = np.average(positionHolder)
        #         averageDifference = mainPeakPositions[i] - wholeAverage
        #         #averageDifference = topAverage - bottomAverage
        #         topDifference = mainPeakPositions[i] - topAverage
        #         bottomDifference = mainPeakPositions[i] - bottomAverage
        #         differenceSign = np.sign(topDifference)
        #         topDifferenceAbs = np.absolute(topDifference)
        #         bottomDifferenceAbs = np.absolute(bottomDifference)
        #         averageDifferenceAbs = np.absolute(averageDifference)
        #         bottomStd = np.std(bottomHalf)
        #         topStd = np.std(topHalf)
        #         wholeStd = np.std(positionHolder)
        #         impinging = False
        #         clamping = False
        #         # differenceTopMode = scistats.mode(differenceSignHolder[0:int(len(differenceSignHolder)/2)])
        #         # differenceBottomMode = scistats.mode(differenceSignHolder[int(len(differenceSignHolder)/2):len(differenceSignHolder)])
        #         if (wholeStd*7 < averageDifferenceAbs):
        #             if (currentMovingMin != pastMovingMin):
        #                 if (currentMovingMax == pastMovingMax):
        #                     newState = stateHolder[len(stateHolder) - 1] + 1
        #                 else:
        #                     newState = stateHolder[len(stateHolder) - 1]
        #             elif (currentMovingMax != pastMovingMax):
        #                 newState = stateHolder[len(stateHolder) - 1] + 1
        #             elif (wholeStd*8 < averageDifference):
        #                 newState = stateHolder[len(stateHolder) - 1] + 1
        #             else:
        #                 newState = stateHolder[len(stateHolder) - 1]
        #         else:
        #             newState = stateHolder[len(stateHolder) - 1]
        #         # if (len(differenceSignHolder) < frameHolderSize):
        #         #     differenceSignHolder.append(differenceSign)
        #         # else:
        #         #     newDifferenceSignHolder = differenceSignHolder[0:(len(differenceSignHolder)-1)]
        #         #     newDifferenceSignHolder.append(differenceSign)
        #         #     differenceSignHolder = newDifferenceSignHolder
        #         stateHolder.append(newState)
        #         newPositionHolder = positionHolder[0:(len(positionHolder)-1)]
        #         newPositionHolder.append(mainPeakPositions[i])
        #         positionHolder = newPositionHolder

        # plt.figure(1)
        # plt.plot(timeStamps, stateHolder)
        #
        # plt.figure(2)
        # plt.plot(timeStamps, bfpStates)
        #
        # plt.figure(3)
        # plt.plot(timeStamps, mainPeakPositions)

        # plt.figure(4)
        # plt.plot(movingTime, movingNormality)

    def setCurrentCycle(self, cycleIndex):
        if self.currentFileData != None:
            self.currentCycleIndex = cycleIndex
            self.currentCycleData = self.currentFileData[cycleIndex]

    def exportCurrentCycleCsvInCurrentFile(self):
        if self.currentFileData != None:
            if self.currentCycleIndex != None:
                if self.currentCycleData != None:
                    csvFileName = self.currentFileName + 'cycleIndex' + str(self.currentCycleIndex) + '.csv'
                    csvFilePath = os.path.join(self.currentDirectory, csvFileName)
                    csvFile = open(csvFilePath, 'w', newline='')

                    fieldNames = ['timeStamp', 'bfpState', 'piezoVoltage', 'peakPixelPosition']

                    cycleWriter = csv.writer(csvFile, dialect='excel')

                    cycleData = self.currentCycleData

                    cycleWriter.writerow(fieldNames)

                    expParameters = np.array(cycleData['experimentParameters'])
                    timeStamps = np.array(cycleData['timeStamps'])
                    bfpStates = np.array(cycleData['bfpStates'])
                    piezoVoltages = np.array(cycleData['piezoVoltages'])
                    mainPeakPositions = np.array(cycleData['mainPeakPositions'])

                    for i in range(0, len(timeStamps)):
                        cycleWriter.writerow([timeStamps[i], bfpStates[i], piezoVoltages[i], mainPeakPositions[i]])

                    csvFile.close()
                    pass

    def movingAverage(self, cycleData, numOfPointsToAverage):
        expParameters = np.array(cycleData['experimentParameters'])
        timeStamps = np.array(cycleData['timeStamps'])
        bfpStates = np.array(cycleData['bfpStates'])
        piezoVoltages = np.array(cycleData['piezoVoltages'])
        mainPeakPositions = np.array(cycleData['mainPeakPositions'])

        timePoints = []
        positionAverages = []
        positionStds = []

        for i in range(0, len(timeStamps)):
            if i < numOfPointsToAverage:
                positionsToAvg = mainPeakPositions[i-numOfPointsToAverage:i]
                positionsAvg = np.average(positionsToAvg)
                positionsStd = np.std(positionsToAvg)
                positionAverages.append(positionsAvg)
                timePoints.append(timePoints[i])
                positionStds.append(positionsStd)

        plt.figure(1)
        plt.plot(timePoints, positionAverages)
        plt.xlabel('Time')
        plt.ylabel('Positions (pixels)')

        plt.show()
        pass
        # zeroTimeStamps = []
        # zeroMainPeakPositions = []
        #
        # for i in range(0, len(timeStamps)):
        #     if bfpStates[i] == 0.00000:
        #         zeroTimeStamps.append(timeStamps[i])
        #         zeroMainPeakPositions.append(mainPeakPositions[i])
        #
        # zeroPeakPosition = self.determineZeroForcePixelPosition(zeroMainPeakPositions)
        # forceArray = self.convertToForce(peakLocation, zeroPeakPosition, expPara)
        # timeArray = np.array(time)
        #
        # averagesDict = self.plusMinusForceAverages(25, timeArray, forceArray)
        # variancesDict = self.plusMinusForceVariances(25, timeArray, forceArray)
        # normalTestDict = self.plusMinusForceNormalTest(25, timeArray, forceArray)

        # zeroStateForceArray = self.convertToForce(zeroState, zeroPeakPosition, expPara)
        # oneStateForceArray = self.convertToForce(oneState, zeroPeakPosition, expPara)
        # twoStateForceArray = self.convertToForce(twoState, zeroPeakPosition, expPara)
        # threeStateForceArray = self.convertToForce(threeState, zeroPeakPosition, expPara)
        # fourStateForceArray = self.convertToForce(fourState, zeroPeakPosition, expPara)
        # fiveStateForceArray = self.convertToForce(fiveState, zeroPeakPosition, expPara)
        #
        # plt.figure(1)
        # plt.plot(zeroStateTime, zeroStateForceArray)
        # plt.plot(oneStateTime, oneStateForceArray)
        # plt.plot(twoStateTime, twoStateForceArray)
        # plt.plot(threeStateTime, threeStateForceArray)
        # plt.plot(fourStateTime, fourStateForceArray)
        # plt.plot(fiveStateTime, fiveStateForceArray)
        # plt.ylabel('Force')
        # plt.xlabel('Time')
        #
        # plt.figure(2)
        # plt.plot(time, bfpState)
        # plt.ylabel('BFP State')
        # plt.xlabel('Time')
        #
        # plt.figure(3)
        # plt.plot(averagesDict['time'], averagesDict['averages'])
        # plt.ylabel('Averages')
        # plt.xlabel('Time')
        #
        # plt.figure(4)
        # plt.plot(variancesDict['time'], variancesDict['variances'])
        # plt.ylabel('Variances')
        # plt.xlabel('Time')
        #
        # plt.figure(5)
        # plt.plot(normalTestDict['time'], normalTestDict['statistics'])
        # plt.ylabel('Statistic')
        # plt.xlabel('Time')
        #
        # plt.figure(6)
        # plt.plot(normalTestDict['time'], normalTestDict['pValues'])
        # plt.ylabel('P value')
        # plt.xlabel('Time')
        #
        # plt.show()
        # pass

    def plusMinusForceAverages(self, plusMinusIndex, timeArray, forceArray):
        averages = []
        for i in range(0, len(timeArray)):
            if (i >= plusMinusIndex/2) and (i < (len(timeArray)-(plusMinusIndex/2))):
                averageForTime = np.average(forceArray[i-plusMinusIndex/2:i+plusMinusIndex/2])
                averages.append(averageForTime)
        averageArray = np.array(averages)
        timeNArray = np.array(timeArray[plusMinusIndex:len(timeArray)])
        averagesDict = {'averages': averageArray, 'time': timeNArray}
        return averagesDict


    def plusMinusForceVariances(self, plusMinusIndex, timeArray, forceArray):
        variances = []
        for i in range(0, len(timeArray)):
            if (i >= plusMinusIndex/2) and (i < (len(timeArray)-(plusMinusIndex/2))):
                varianceForTime = np.var(forceArray[i-plusMinusIndex/2:i+plusMinusIndex/2])
                variances.append(varianceForTime)
        varianceArray = np.array(variances)
        timeNArray = np.array(timeArray[plusMinusIndex:len(timeArray)])
        variancesDict = {'variances': varianceArray, 'time': timeNArray}
        return variancesDict

    def plusMinusForceNormalTest(self, plusMinusIndex, timeArray, forceArray):
        statistics = []
        pValues = []

        for i in range(0, len(timeArray)):
            if (i >= plusMinusIndex/2) and (i < (len(timeArray)-(plusMinusIndex/2))):
                normalTestForTime = scistats.normaltest(forceArray[i-plusMinusIndex/2:i+plusMinusIndex/2])
                statistics.append(normalTestForTime.statistic)
                pValues.append(normalTestForTime.pvalue)
        statisticArray = np.array(statistics)
        pValueArray = np.array(pValues)
        timeNArray = np.array(timeArray[plusMinusIndex:len(timeArray)])
        normalTestDict = {'statistics': statisticArray, 'time': timeNArray, 'pValues': pValueArray}
        return normalTestDict

    def parseFilesInDirectory(self):
        if self.currentDirectory != None:
            fileList = os.listdir(self.currentDirectory)
            for file in fileList:
                currentPath = os.path.join(self.currentDirectory, file)
                if os.path.isdir(currentPath):
                    pass
                if os.path.isfile(currentPath):
                    self.currentFile = open(currentPath, 'r')
                    self.currentFileName = file
                    self.parseFile()

    def parseFileInDirectory(self, fileName):
        if self.currentDirectory != None:
            fileList = os.listdir(self.currentDirectory)
            for file in fileList:
                if file == fileName:
                    currentPath = os.path.join(self.currentDirectory, file)
                    if os.path.isdir(currentPath):
                        pass
                    if os.path.isfile(currentPath):
                        self.currentFile = open(currentPath, 'r')
                        self.currentFileName = fileName
                        self.parseFile()

    def setCurrentFile(self, fileName):
        if self.currentDirectory != None:
            fileList = os.listdir(self.currentDirectory)
            for file in fileList:
                if file == fileName:
                    currentPath = os.path.join(self.currentDirectory, file)
                    if os.path.isdir(currentPath):
                        pass
                    if os.path.isfile(currentPath):
                        self.currentFileName = fileName
                        self.currentFile = open(currentPath, 'r')

    def setCurrentFileDirectory(self, dataDirectory):
        if os.path.isdir(dataDirectory):
            self.currentDirectory = dataDirectory

    def runAnalysisOnCycle(self, analysisType, cycleData):
        pass

    def saveCurrenFileDataIntoPickle(self):
        if self.currentDirectory != None:
            pickleFileName = self.currentFileName + '.pickle'
            path = os.path.join(self.currentDirectory, pickleFileName)
            file = open(path, 'wb')
            pickleDump = pickle.dumps(self.currentFileData)
            file.write(pickleDump)
            file.close()
        else:
            if self.currentFileName != None:
                pickleFileName = self.currentFileName + '.pickle'
                file = open(pickleFileName, 'wb')
                pickleDump = pickle.dumps(self.currentFileData)
                file.write(pickleDump)
                file.close()

    def loadFileDataFromPickle(self, fileName):
        if self.currentDirectory != None:
            path = os.path.join(self.currentDirectory, fileName)
            if os.path.isfile(path):
                file = open(path, 'rb')
                self.currentFileName = fileName[0:(len(fileName)-7)]
                self.currentFileData = pickle.loads(file.read())
        else:
            if os.path.isfile(fileName):
                file = open(fileName, 'rb')
                self.currentFileData = pickle.loads(file.read())

    def __init__(self):
        pass


dataApi = BFPData()
dataApi.setCurrentFileDirectory('../SampleData')
#dataApi.parseFilesInDirectory()
#dataApi.setCurrentFile('20151201_GC-VWF_17-1_2')
#dataApi.parseFile()
#dataApi.saveCurrenFileDataIntoPickle()
dataApi.loadFileDataFromPickle('20151201_GC-VWF_17-1_2.pickle')
#dataApi.setCurrentCycle(51)
#dataApi.exportCurrentCycleCsvInCurrentFile()
dataApi.analyzeCycleInCurrentFile(51)