from bitarray import bitarray
from bitarray.util import int2ba, ba2int
from math import floor
word_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]


class svNavMessage:
    def __init__(self):
        self.__page_position = 0
        self.__subFramePosition = 0
        self.__data_subframe = [None for i in range(15)]
        self.__data_dataFrame = [[None, None, None] for i in range(24)]#As I/NAV message is composed of 24 sub-Frames, it is planned to add constraints here to have up to 24 frames
        self.__onsma_dataFrame = [[None, None, None] for i in range(24)]
        self.__osnma_subframe = [None for i in range(15)]
        self.__pageDummy = False
        self.__dataFrameCompleteStatus = False
        self.__OsnmaDistributionStatus = False
        self.__wordType = bytearray()
        self.__t0Time = bytearray()
        self.__t0Timenatural = str()
    def subFrameSequence(self,wordType=int,data=bytearray(),osnma=bytearray()):
        if self.__dataFrameCompleteStatus:
                self.__data_subframe = [None for i in range(15)]
                self.__osnma_subframe  = [None for i in range(15)]
        if wordType == 63:
            self.__pageDummy = True #Word Type as value 11111 (or 63) is considered as dummmy Page
            self.__dataFrameCompleteStatus = False
        else:
            self.__pageDummy = False
            if wordType in word_types_sequence[self.__page_position]:# In Sync
                self.__data_subframe[self.__page_position]=data
                self.__osnma_subframe[self.__page_position]=osnma
                if self.__page_position <  len(word_types_sequence)-1: #In Sync not complete
                    self.__page_position += 1
                    self.__dataFrameCompleteStatus = False
                else: #In Sync & Complete
                    self.__page_position = 0
                    self.__dataFrameCompleteStatus = True
                    self.__OsnmaDistributionStatus = not all(element == b'\x00\x00\x00\x00\x00' for element in self.__osnma_subframe)
                if wordType == 5: # to get the Time
                    b = bitarray()
                    b.frombytes(data)
                    GST_current_WN = b[73:85]
                    GST_current_TOW = b[85:105]
                    GST_t0_TOW_int = ba2int(GST_current_TOW)-25 #we need to go up to the start of the Sub-Frame, and word 5 is 
                    GST_t0_TOW = int2ba(GST_t0_TOW_int,20)
                    GST_t0 = GST_current_WN+GST_t0_TOW
                    self.__t0Time = GST_t0.tobytes()
                    self.__t0TimeNatural = self.weekSeconds2Time(GST_t0_TOW_int)
                if self.__dataFrameCompleteStatus:
                    #We keep appending values. For future implementaiton, chec
                    self.__data_dataFrame.append([self.__t0TimeNatural,self.__t0Time,self.__data_subframe])
                    self.__data_dataFrame.pop(0)
                    self.__onsma_dataFrame.append([self.__t0TimeNatural,self.__t0Time,self.__osnma_subframe])
                    self.__onsma_dataFrame.pop(0)
            else:
                self.__page_position = 0 #OUT OF SYNC
                self.__dataFrameCompleteStatus = False
                self.__data_subframe = [None for i in range(15)]
                self.__osnma_subframe  = [None for i in range(15)]
    def weekSeconds2Time(self,weekSeconds): #function to return a string of hours in HH:mm:ss (to be updated)
        hours = weekSeconds/3600
        while hours >= 24:
            hours = hours - 24
        hour = int(hours)
        minutes = hours-hour #minutes in hour format
        minute = minutes*60  #minuts in minut format
        seconds = minute - int (minute) # seconds in minut format
        second = int(seconds*60) #seconds in second format
        millis = seconds*60 - int(seconds*60)
        time = str(hour).zfill(2) + ":" + str(int(minute)).zfill(2) + ":" + str(second).zfill(2) + "."+str(millis)
        return  time
    def setDataFrameCompleteStatus(self, status = bool()):
        self.__dataFrameCompleteStatus = status
        self.__data_dataFrame.append([self.__t0TimeNatural,self.__t0Time,self.__data_subframe])
        self.__data_dataFrame.pop(0)
    def getDataOnGST(self,gst):
        for  item in self.__data_dataFrame:
            if (item[1] == gst) and gst is not None:
                return item[2]
    def getOsnmaOnGST(self,gst=bytearray()):
        for item in self.__onsma_dataFrame:
            if (item[1] == gst) and gst is not None:
                return item[2]
    def getSVId(self):
        return self.__sv_id
    def getPagePosition(self):
        return self.__page_position
    def getOsnmaDistributionStatus(self):
        return self.__OsnmaDistributionStatus
    def getDataFrameCompleteStatus(self):
        return self.__dataFrameCompleteStatus
    def getDataSubframe(self):
        return self.__data_subframe
    def getDataFrame(self):
        return self.__data_dataFrame
    def getDataFrameTime(self):
        return self.__data_dataFrameTime
    def getOsnmaSubFrame(self):
        return self.__osnma_subframe
    def getOsnmaFrame(self):
        return self.__onsma_dataFrame
    def getT0Natural(self):
        return self.__t0TimeNatural
    def getT0(self):
        return self.__t0Time


class svKrootOsnmaMack:
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
        b = bitarray()
        b.frombytes(self.__hkroot[1])
        self.__DSMId = b[0:4].tobytes()
        self.__DSMBlockId = b[-4:].tobytes()
        self.__DSMBlock = self.__hkroot[2:]
    def getCID(self):
        return self.__CID
    def getDSMBlockId(self):
        return self.__DSMBlockId
    def getDSMId(self):
        return self.__DSMId
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


class svConstellation(svNavMessage):
    def __init__(self,numSV):
        self.__numSv = numSV
        self.__sv = [[None,None] for i in range(self.__numSv)]
        for i in range(numSV): 
            self.__sv[i][0] = i+1
            self.__sv[i][1] = svNavMessage()
    def getSvDataFrameCompleteStatus(self,svId):
        return self.__sv[svId-1][1].getDataFrameCompleteStatus()
    def getSvDataFrame(self,svId):
        return self.__sv[svId-1][1].getDataFrame()
    def getSvNavMessageObject(self, svId):
        return self.__sv[svId-1][1]
    def getSvDataSubFrame(self, svId):
        return self.__sv[svId-1][1].getDataSubframe()
    def getSvOsnmaDistributionStatus(self, svId):
        return self.__sv[svId-1][1].getOsnmaDistributionStatus()
    def getSvGST(self, svId):
        return self.__sv[svId-1][1].getT0()
    def getSvDataOnGST(self, svId, GST):
        return self.__sv[svId-1][1].getDataOnGST(GST)
    def getSvOsnmaOnGST(self, svId, GST):
        return self.__sv[svId-1][1].getOsnmaOnGST(GST)
    def feedConstellation(self,svId=int,wordType=int,data=bytes(),osnma=bytes()):
        self.__sv[svId-1][1].subFrameSequence(wordType, data, osnma)
    def notifier(self):
        svCompleted = []
        for i in range(self.__numSv):
            if self.__sv[i][1].getDataFrameCompleteStatus():
                svCompleted.append(self.__sv[i][0])
        return svCompleted
        


class NavMessageAuthenticator:
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
        self.__mackReserved2 = self.__concatenedMack[-4:].tobytes()
        self.__numTags = floor((480-keyLength)/(tagLength+16)) - 1
        self.__ParsedMackMsg["Tag0"] = self.__tag0
        self.__ParsedMackMsg["MACSEQ"] = self.__MACSEQ
        #missing rest of the Tags (needed for cross-authentication)
        startKeyPosition = tagLength+12+4+(tagLength+16)*self.__numTags
        self.__teslaKey = self.__concatenedMack[startKeyPosition:(startKeyPosition+keyLength)].tobytes()
        self.__ParsedMackMsg["Tesla Key"] = self.__teslaKey
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
