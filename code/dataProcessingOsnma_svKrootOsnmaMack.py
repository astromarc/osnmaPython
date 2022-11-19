from bitarray import bitarray
from bitarray.util import int2ba, ba2int, ba2hex
from math import floor
#import logging
class mackParser:
    def __init__(self):
        self.__ParsedMackMsg = {}
        self.__tag0 = bitarray()
        self.__MACSEQ = bitarray()
        self.__mackReserved2 = bitarray()
        self.__numTags = 0
    def parseMackMessage(self,mack,keyLength, tagLength):
        self.__concatenedMack = bitarray()
        for mack_part in mack:
            b = bitarray()
            b.frombytes(mack_part)
            self.__concatenedMack += b
        self.__tag0 = self.__concatenedMack[0:tagLength].tobytes()
        self.__MACSEQ = self.__concatenedMack[tagLength:(tagLength+12)].tobytes()
        self.__mackReserved2 = self.__concatenedMack[(tagLength+12):(tagLength+12+4)].tobytes()
        self.__numTags = floor((480-keyLength)/(tagLength+16)) - 1
        self.__ParsedMackMsg["Tag0"] = self.__tag0
        self.__ParsedMackMsg["MACSEQ"] = self.__MACSEQ
        #missing rest of the Tags (needed for cross-authentication)
        startKeyPosition = tagLength+12+4+(tagLength+16)*self.__numTags
        self.__teslaKey = self.__concatenedMack[startKeyPosition:(startKeyPosition+keyLength)].tobytes()
        self.__ParsedMackMsg["Tesla Key"] = self.__teslaKey
        next_index = tagLength + 16
        self.__tags_and_info = []
        for i in range(self.__numTags):
            ti = {}
            ti["Tag"] = self.__concatenedMack[next_index:(next_index+tagLength)].tobytes()
            ti["Tag-Info"] = self.__concatenedMack[(next_index+tagLength):(next_index+tagLength+16)]
            ti["PRND"] = ba2int(ti["Tag-Info"][0:8])
            ti["ADKD"] = ba2int(ti["Tag-Info"][8:12])
            ti["Reserved2"] = ti["Tag-Info"][12:].tobytes()
            ti["Tag-Info"] = ti["Tag-Info"].tobytes()
            self.__tags_and_info.append(ti)
            next_index += tagLength + 16
        #logging.info("Tesla Key received with value: "+ str((self.__teslaKey).hex()))
    def getConcatenedMack(self):
        return self.__concatenedMack.tobytes()
    def getTag0(self):
        return self.__tag0
    def getMacSeq(self):
        return self.__MACSEQ
    def getMackReserved2(self):
        return self.__mackReserved2
    def getParsedMackMessage(self):
        return self.__ParsedMackMsg
    def getTeslaKey(self):
        return self.__teslaKey
    def getTagsAndInfo(self):
        return self.__tags_and_info

class osnmaSplitter:
    def __init__(self):
        self.__CID = int()
        self.__DSMBlockId = bytearray()
        self.__DSMId = bytearray()
        self.__CDPKS = int()
        self.__NMAS = int()
        self.__reservedNMA = bytearray()
        self.__hkroot = [None for i in range(15)]
        self.__mack = [None for i in range(15)]
        self.__DSMBlock = [None for i in range(13)]
        self.__parsedMack = {}
    def osnmaSubFrame2hkRootMack(self, osnmaSubFrame):
        self.__hkroot = [None for i in range(15)]
        self.__mack = [None for i in range(15)]
        self.__DSMBlock = [None for i in range(13)]
        for osnmaPage in osnmaSubFrame:
            b = bitarray()
            b.frombytes(osnmaPage)
            self.__hkroot.append(b[0:8].tobytes())
            self.__hkroot.pop(0)
            self.__mack.append(b[-32:].tobytes())
            self.__mack.pop(0)
        b = bitarray()
        b.frombytes(self.__hkroot[0])
        self.__NMAS = ba2int(b[0:2])
        self.__CID = ba2int(b[2:4])
        self.__CDPKS = ba2int(b[4:7])
        self.__reservedNMA = b[7]
        self.__nmaHeader = b[0:8]
        b = bitarray()
        b.frombytes(self.__hkroot[1])
        self.__DSMId = b[0:4]
        self.__DSMBlockId = b[-4:]
        self.__DSMBlock = self.__hkroot[2:]
        
    def getCID(self):
        return self.__CID
    def getDSMBlockId(self):
        return ba2int(self.__DSMBlockId)
    def getDSMId(self):
        return ba2int(self.__DSMId)
    def getCDPKS(self):
        return self.__CDPKS
    def getHkroot(self):
        return self.__hkroot
    def getMack(self):
        return self.__mack
    def getNMAS(self):
        return self.__NMAS
    def getReservedNMA(self):
        return self.__reservedNMA
    def getDSMBlock(self):
        return self.__DSMBlock
    def getNMAHeader(self):
        return self.__nmaHeader