from bitarray import bitarray
from bitarray.util import int2ba, ba2int, ba2hex
from math import floor
from dataProcessingOsnma_DSM import DSMMessage
import logging


word_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]


class svNavMessage:
    def __init__(self, svid):
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
        self.__sv_id = svid
        self.__sv_osnma_status = 1
        self.__subFrameProgress = self.__page_position / len(word_types_sequence)
    def subFrameSequence(self,wordType=int,data=bytearray(),osnma=bytearray()):
        if wordType == 63:
            self.__pageDummy = True #Word Type as value 11111 (or 63) is considered as dummmy Page
            self.__page_position = 0
        else:
            self.__pageDummy = False
            if wordType in word_types_sequence[self.__page_position]:# In Sync
                self.__data_subframe[self.__page_position]=data
                self.__osnma_subframe[self.__page_position]=osnma
                self.__OsnmaDistributionStatus = not all(element == b'\x00\x00\x00\x00\x00' for element in self.__osnma_subframe)
                if not self.__OsnmaDistributionStatus: 
                    self.__sv_osnma_status = 2
                if wordType == 5: # to get the Time
                    b = bitarray()
                    b.frombytes(data)
                    GST_current_WN = b[73:85]
                    GST_current_TOW = b[85:105]
                    GST_t0_TOW_int = ba2int(GST_current_TOW)-25 #we need to go up to the start of the Sub-Frame, and word 5 is 25 seconds delayed
                    GST_t0_TOW = int2ba(GST_t0_TOW_int,20)
                    GST_t0 = GST_current_WN+GST_t0_TOW
                    self.__t0Time = GST_t0.tobytes()
                    self.__t0TimeNatural = self.weekSeconds2Time(GST_t0_TOW_int)
                self.__subFrameProgress = (self.__page_position+1) / (len(word_types_sequence))
                self.__page_position += 1
                
                if self.__page_position == len(word_types_sequence): self.__dataFrameCompleteStatus = True
                else: self.__dataFrameCompleteStatus = False
                
            else:
                self.__page_position = 0 #OUT OF SYNC
                self.__data_subframe = [None for i in range(15)]
                self.__osnma_subframe  = [None for i in range(15)]
                self.__subFrameProgress = 0
            if self.__dataFrameCompleteStatus:
                    #We keep appending values. For future implementaiton, check how much do we want to add in the Frame ()
                    self.__page_position = 0
                    self.__data_dataFrame.append([self.__t0TimeNatural,self.__t0Time,self.__data_subframe])
                    self.__data_dataFrame.pop(0)
                    self.__onsma_dataFrame.append([self.__t0TimeNatural,self.__t0Time,self.__osnma_subframe])
                    self.__onsma_dataFrame.pop(0)
                    self.log()
            
    def getOsnmaStatus(self):
        return self.__OsnmaDistributionStatus
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
    def getT0Seconds(self):
        b = bitarray()
        b.frombytes(self.__t0Time)
        wn = ba2int(b[0:12])*604800 # week to seconds
        tow = ba2int(b[12:])
        return wn+tow
    def log(self):
        if self.__OsnmaDistributionStatus:
            logging.info("SV"+str(self.__sv_id)+" completed SubFrame and Transmits OSNMA")
        else:
            logging.info("SV"+str(self.__sv_id)+" completed SubFrame and Does Not Transmits OSNMA")
    def getSubFrameProgress(self):
        return self.__subFrameProgress
    def setDataFrameCompleteStatus(self,status):
        if status == True:
            self.__dataFrameCompleteStatus = True
        else:
            self.__dataFrameCompleteStatus = False
            self.__page_position = 0


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


class svConstellation():
    def __init__(self,numSV):
        self.__numDSM = 15 # According to ICD DSM ID can only take values from 0 to 15 (see section 3.2.1)
        self.__numSv = numSV
        self.__sv = [[None,None, None,[None,None]] for i in range(self.__numSv)]
        self.__DSM = [[None, None] for i in range(self.__numDSM)]
        for i in range(numSV): 
            self.__sv[i][0] = i+1 #svId
            self.__sv[i][1] = svNavMessage(i+1) # NavigationMessage and Osnma Logic and Storing
            self.__sv[i][2] = None # Self-Authentication Status
            self.__sv[i][3] = [None,None] #Cross-Authentication SV and Status
        for i in range(self.__numDSM):
            self.__DSM[i][0] = i
            self.__DSM[i][1] = DSMMessage(i)
    def getSvDataFrameCompleteStatus(self,svId):
        return self.__sv[svId-1][1].getDataFrameCompleteStatus()
    def getSvDataFrame(self,svId):
        return self.__sv[svId-1][1].getDataFrame()
    def getSvOsnmaFrame(self,svId):
        return self.__sv[svId-1][1].getOsnmaFrame()
    def getSvNavMessageObject(self, svId):
        return self.__sv[svId-1][1]
    def getSvDataSubFrame(self, svId):
        return self.__sv[svId-1][1].getDataSubframe()
    def getSvOsnmaDistributionStatus(self, svId):
        return self.__sv[svId-1][1].getOsnmaDistributionStatus()
    def getSvOsnmaStatus(self, svId):
        return self.__sv[svId-1][1].getOsnmaStatus()
    def getSvGST(self, svId):
        return self.__sv[svId-1][1].getT0()
    def getSvDataOnGST(self, svId, GST):
        return self.__sv[svId-1][1].getDataOnGST(GST)
    def getSvOsnmaOnGST(self, svId, GST):
        return self.__sv[svId-1][1].getOsnmaOnGST(GST)
    def getSvSvId(self, svId):
        return self.__sv[svId-1][0]
    def getSVSubFrameProgress(self, svId):
        return self.__sv[svId-1][1].getSubFrameProgress()
    def feedConstellation(self,svId=int,wordType=int,data=bytes(),osnma=bytes()):
        self.__sv[svId-1][1].subFrameSequence(wordType, data, osnma)
    def feedDSM(self, DSM_ID, DSM_BID, DSM_Block):
        DSM = (self.__DSM[DSM_ID])[1]
        DSM.addBlock(DSM_BID,DSM_Block)
        self.__lastDSMId = DSM_ID
    def getCurrentDSMId(self):
        return self.__lastDSMId
    def getCurrentDSMBlocks(self):
        return self.__DSM[self.__lastDSMId][1].getCurrBlocks()
    def getCurrentTotalDSMBlocks(self):
        return self.__DSM[self.__lastDSMId][1].getNumBlocks()
    def getCurrentDSMCompletenessStatus(self):
        return self.__DSM[self.__lastDSMId][1].isComplete()
    def getSvNum(self):
        return self.__numSv
    def getCurrentKroot(self):
        return self.__DSM[self.__lastDSMId][1].getKroot()
    def getCurrentKrootTime(self):
        return self.__DSM[self.__lastDSMId][1].getKrootTime()
    def getCurrentKrootTimeSeconds(self):
        return self.__DSM[self.__lastDSMId][1].getKrootTimeSeconds()
    def getCurrentKeySize(self):
        return self.__DSM[self.__lastDSMId][1].getKrootSize()
    def getCurrentTagSize(self):
        return self.__DSM[self.__lastDSMId][1].getTagSize()
    def getCurrentAlpha(self):
        return (self.__DSM[self.__lastDSMId][1].getAlpha()).tobytes()
    def getCurrentM(self,NMAHeader):
        return self.__DSM[self.__lastDSMId][1].getM(NMAHeader)
    def getSvT0Seconds(self,svId):
        return self.__sv[svId-1][1].getT0Seconds()
    def getCurrentDS(self):
        return self.__DSM[self.__lastDSMId][1].getDS()
    def setSvDataFrameCompleteStatus(self, svId, status):
        return self.__sv[svId-1][1].setDataFrameCompleteStatus(status)
    def setSvSelfAuthenticationStatus(self, svId, svOsnmaSelfStatus):
        self.__sv[svId-1][2] = svOsnmaSelfStatus
    def getSvSelfAuthenticationStatus(self, svId):
        return self.__sv[svId-1][2]
    def setSvCrossAuthentication(self, svId,crossAuthentication):
        for item in crossAuthentication:
            if item is not None:
                PRND = item[0]
                status = item[1]
                if status != None:
                    if PRND == 255 or PRND == svId: # we consider this as self authentication
                        self.setSvSelfAuthenticationStatus(svId, status)
                    else:
                        self.__sv[PRND-1][3] = [svId, status]
    def getSvCrossAuthenticationStatus(self, svId):
        return self.__sv[svId-1][3]