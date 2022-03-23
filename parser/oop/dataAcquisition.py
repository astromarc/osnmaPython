from abc import ABC, abstractmethod
import csv
from serial import Serial
from pyubx2 import UBXReader

class getUbloxWords(ABC):
    '''
    class description
    '''
    @abstractmethod
    def getUbloxWordsList(self):
        pass

class readUbloxData(getUbloxWords):
    '''
    class description
    '''
    def __init__(self,filename,delimiter):
        self.__filename = filename
        self.__delimeter = delimiter
        self.__file = open(self.__filename)
    def getUbloxWordsList(self):
        return self.__file.readline().split(self.__delimeter)
    def closeFile(self):
        try: self.__file.close()
        except: print("File ",self.__file," cannot be closed")
    def openFile(self):
        self.__file = open(self.__filename)


class readUbloxSerial(getUbloxWords):
    '''
    class description
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
