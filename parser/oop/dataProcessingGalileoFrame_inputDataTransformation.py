from bitarray import bitarray
from bitarray.util import int2ba, ba2int

class ubloxWordsList2GalileoICD:
    def ublox2Galileo(self,ubloxList):
        self.__evenPage = bitarray()
        self.__oddPage = bitarray()
        self.__ubloxList = ubloxList
        self.__svId = int(self.__ubloxList[1])
        for idx, word in enumerate(self.__ubloxList[8:len(self.__ubloxList)-1]):
            if idx < 4:
                word2ba = int2ba(int(word),32)
                self.__evenPage += word2ba
            else:
                word2ba = int2ba(int(word),32)
                self.__oddPage += word2ba
        self.__page = self.__oddPage + self.__oddPage
        self.processEvenPage()
        self.processOddPage()
        self.__data = self.__dataK + self.__dataJ
    def processEvenPage(self):
        self.__evenEvenOdd = self.__evenPage[0]
        self.__evenPagType = self.__evenPage[1]
        self.__wordType = self.__evenPage[2:8]
        self.__dataK = self.__evenPage[2:114] # 6 first bit of dataK is WordType
        self.__evenTail = self.__evenPage[114:120]
        self.__evenGalileo = self.__evenPage[0:120]
    def processOddPage(self):
        self.__oddEvenOdd = self.__oddPage[0]
        self.__oddPagType = self.__oddPage[1]
        self.__dataJ = self.__oddPage[2:18]
        self.__osnma = self.__oddPage[18:58]
        self.__SAR = self.__oddPage[58:80]
        self.__spare = self.__oddPage[80:82]
        self.__CRC = self.__oddPage[82:106]
        self.__reserved2 = self.__oddPage[106:114]
        self.__oddTail = self.__oddPage[114:120]
        self.__oddGalileo = self.__oddPage[0:120]
    def getWordType(self):
        return ba2int(self.__wordType)
    def getData(self):
        return self.__data.tobytes()
    def getOsnma(self):
        return self.__osnma.tobytes()
    def getSAR(self):
        return self.__SAR.tobytes()
    def getCRC(self):
        return self.__CRC.tobytes()
    def getSpare(self):
        return self.__spare.tobytes()
    def getSvId(self):
        return self.__svId
    def getReserves2(self):
        return self.__reserved2.tobytes()
    def getDataJ(self):
        return self.__dataJ.tobytes()
    def getDataK(self):
        return self.__dataK.tobytes()
    def getPage(self):
        return self.__page.tobytes()