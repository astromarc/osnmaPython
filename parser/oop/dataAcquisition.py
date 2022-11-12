from abc import ABC, abstractmethod
import csv
from serial import Serial
from pyubx2 import UBXReader

class getUbloxWords(ABC):
    '''
    Interface to force the use the method "getUbloxWordList" regardless the input (CSV from test data or serial port data)
    '''
    @abstractmethod
    def getUbloxWordsList(self):
        pass

class readUbloxData(getUbloxWords):
    '''
Class that reads a CSV file and returns a list of words. Similar to "next line" method for iter() objects in Python.
When it is instantiated, it has the following attributes, all of them set when generating the object:
    - filename: String, name of the file you wanna read, e.g., "test.csv"
    - delimeter: String, name of the delimerer, eg., ","
It has the following methods:
    - getUbloxWordsList: method that gives you the next line in a CSV file
    - closeFile: Close the file
    - openFile: Open the file
    - getFileRead: get the filename

    '''
    def __init__(self,filename,delimiter):
        self.__filename = filename
        self.__delimeter = delimiter
        with open(self.__filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            self.__list = list(reader)
        self.__fileRead = True
        self.__index = - 1
    def getUbloxWordsList(self):
        if self.__index < len(self.__list)-1:
            self.__index+=1
            return self.__list[self.__index]
        else: return None
    def closeFile(self):
        try: self.__file.close()
        except: print("File ",self.__file," cannot be closed")
    def openFile(self):
        self.__file = open(self.__filename)
    def getFileRead(self):
        return self.__fileRead 

class readUbloxSerial(getUbloxWords):
    '''
Class that reads the input data from a Ublox Receiver and returns a list of Ublox Words.
When it is instantiated, it has the following attributes, all of them set when generating the object:
    - filename: String, e.g., 'Test.csv'. Only used if you want to record the data received
    - COMPort: String e.g., 'COM9'. Serial Port in which your Ublox Receiver is connected
    - boudRate: integer, e.g. 9600. BoudRate of your Serial Port (has to be the same as the one set in the uBlox Receiver)
    - record: bool, e.g., True. True if you want to record the data received in a CSV.
It has the following methods:
    - getUbloxWordList: when this method is invoked, the object waits until it receives a dataStream from the input port and sends back a list of uBlox Words.
    - saveUbloxWordsList: method to save into a CSV the data received. Authomatically called by getUbloxWordList if object is instantiated with 'record' True.

    '''
    def __init__(self,filename,COMPort,boudRate,record):
        self.__filename = filename
        self.__COMPort = COMPort
        self.__boudRate = boudRate
        self.__record = False
    def getUbloxWordsList(self):
        ubxPages = []
        stream = Serial(self.__COMPort, self.__boudRate, bytesize=8, parity='N', stopbits=1,)
        ubr = UBXReader(stream)
        (raw_data, parsed_data) = ubr.read()
        if parsed_data is not None:
            ubxPages = str(parsed_data).split(",")
        stream.close()
        for x in ubxPages:
            if x != "<UBX(RXM-SFRBX":
                ubxSplit = x.split('=')[1].split(")")[0]
                ubxPages.append(ubxSplit)
        if self.__record: self.saveUbloxWordsList(ubxPages)
        return ubxPages
    def saveUbloxWordsList(self,ubxPages):
        with open(self.__filename, 'a', newline='') as f:
            f.write(ubxPages.join())
            f.write('\n')
            f.close()