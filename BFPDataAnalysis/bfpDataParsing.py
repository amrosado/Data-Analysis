__author__ = 'arosado'
import csv
import os

class BFPData:
    currentDirectory = None
    currentFile = None

    def parseFile(self):
        fileText = self.currentFile.read()
        fileLines = fileText.split('\n')
        for line in fileLines:
            lineData = line.split('\t')
            for data in lineData:
                pass

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