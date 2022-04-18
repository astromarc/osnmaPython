from bitarray import bitarray
from bitarray.util import int2ba, ba2int


class galPages2galParameters:
    def processEvenPage(self,evenPage):
        self.__evenEvenOdd = evenPage[0]
        self.__evenPagType = evenPage[1]
        self.__wordType = evenPage[2:8]
        self.__dataK = evenPage[2:114] # 6 first bit of dataK is WordType
        self.__evenTail = evenPage[114:120]
        self.__evenGalileo = evenPage[0:120]
        return self.__evenEvenOdd, self.__evenPagType, self.__wordType, self.__dataK, self.__evenTail, self.__evenGalileo
    def processOddPage(self,oddPage):
        self.__oddEvenOdd = oddPage[0]
        self.__oddPagType = oddPage[1]
        self.__dataJ = oddPage[2:18]
        self.__osnma =oddPage[18:58]
        self.__SAR = oddPage[58:80]
        self.__spare = oddPage[80:82]
        self.__CRC = oddPage[82:106]
        self.__reserved2 = oddPage[106:114]
        self.__oddTail = oddPage[114:120]
        self.__oddGalileo = oddPage[0:120]
        return self.__oddEvenOdd, self.__oddPagType, self.__dataJ, self.__osnma, self.__SAR, self.__spare, self.__CRC, self.__reserved2, self.__oddTail, self.__oddGalileo

class ubloxWordsList2GalileoICD(galPages2galParameters):
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
        self.__evenEvenOdd, self.__evenPagType, self.__wordType, self.__dataK, self.__evenTail, self.__evenGalileo = self.processEvenPage(self.__evenPage)
        self.__oddEvenOdd, self.__oddPagType, self.__dataJ, self.__osnma, self.__SAR, self.__spare, self.__CRC, self.__reserved2, self.__oddTail, self.__oddGalileo = self.processOddPage(self.__oddPage)
        self.__data = self.__dataK + self.__dataJ
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
    def getOddPage(self):
        return self.__oddPage.tobytes()
    def getEvenPage(self):
        return self.__evenPage.tobytes()

class testVectors2GalileoICD(galPages2galParameters):
    def testVec2Galileo(self,evenPage,oddPage):
        self.__evenPage = int2ba(evenPage,120)
        self.__oddPage = int2ba(oddPage,120)
        self.__page = self.__oddPage + self.__evenPage
        self.__evenEvenOdd, self.__evenPagType, self.__wordType, self.__dataK, self.__evenTail, self.__evenGalileo = self.processEvenPage(self.__evenPage)
        self.__oddEvenOdd, self.__oddPagType, self.__dataJ, self.__osnma, self.__SAR, self.__spare, self.__CRC, self.__reserved2, self.__oddTail, self.__oddGalileo = self.processOddPage(self.__oddPage)
        self.__data = self.__dataK + self.__dataJ
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
    
    
