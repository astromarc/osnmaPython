from bitarray import bitarray
from bitarray.util import int2ba, ba2int
import logging

def processEvenPage(evenPage):
    evenEvenOdd = evenPage[0]
    evenPagType = evenPage[1]
    wordType = evenPage[2:8]
    dataK = evenPage[2:114] # 6 first bit of dataK is WordType
    evenTail = evenPage[114:120]
    evenGalileo = evenPage[0:120]
    return evenEvenOdd, evenPagType, wordType, dataK, evenTail, evenGalileo
def processOddPage(oddPage):
    oddEvenOdd = oddPage[0]
    oddPagType = oddPage[1]
    dataJ = oddPage[2:18]
    osnma =oddPage[18:58]
    SAR = oddPage[58:80]
    spare = oddPage[80:82]
    CRC = oddPage[82:106]
    reserved2 = oddPage[106:114]
    oddTail = oddPage[114:120]
    oddGalileo = oddPage[0:120]
    return oddEvenOdd, oddPagType, dataJ, osnma, SAR, spare, CRC, reserved2, oddTail, oddGalileo


class ubloxWordsList2GalileoICD():
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
        self.__page = self.__evenPage[:120] + self.__oddPage[:120]
        self.__evenEvenOdd, self.__evenPagType, self.__wordType, self.__dataK, self.__evenTail, self.__evenGalileo = processEvenPage(self.__evenPage)
        self.__oddEvenOdd, self.__oddPagType, self.__dataJ, self.__osnma, self.__SAR, self.__spare, self.__CRC, self.__reserved2, self.__oddTail, self.__oddGalileo = processOddPage(self.__oddPage)
        self.__data = self.__dataK + self.__dataJ
        logging.info("SV"+str(self.__svId)+" received page "+str(ba2int(self.__wordType)))
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

class testVectors2GalileoICD():
    def testVec2Galileo(self,evenPage,oddPage):
        self.__evenPage = int2ba(evenPage,120)
        self.__oddPage = int2ba(oddPage,120)
        self.__page = self.__oddPage + self.__evenPage
        self.__evenEvenOdd, self.__evenPagType, self.__wordType, self.__dataK, self.__evenTail, self.__evenGalileo = processEvenPage(self.__evenPage)
        self.__oddEvenOdd, self.__oddPagType, self.__dataJ, self.__osnma, self.__SAR, self.__spare, self.__CRC, self.__reserved2, self.__oddTail, self.__oddGalileo = processOddPage(self.__oddPage)
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
    
    
