from bitarray import bitarray
from bitarray.util import int2ba, ba2int
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
                    GST_current_WN = b[0:12]
                    GST_current_TOW = b[85:105]
                    GST_t0_TOW_int = ba2int(GST_current_TOW)-25 #we need to go up to 
                    GST_t0_TOW = int2ba(GST_t0_TOW_int)
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
        time = str(hour).zfill(2) + ":" + str(int(minute)).zfill(2) + ":" + str(second).zfill(2)
        return  time
    def getDataOnGST(self,gst=bytearray()):
        for  item in self.__data_dataFrame:
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
        self.__CID = bytearray()
        self.__DSMBlockId = bytearray()
        self.__DSMId = bytearray()
        self.__DSKPKS = bytearray()
        self.__hkroot = [None for i in range(15)]
        self.__mack = [None for i in range(15)]
    def osnmaSubFrame2hkRootMack(self, osnmaSubFrame=[]):
        self.__hkroot = [None for i in range(15)]
        self.__mack = [None for i in range(15)]
        # for osnmaPage in osnmaSubFrame: TBW
        #     hkroot.append(osnmaPage)
    def getCID(self):
        return self.__CID
    def getDSMBlockId(self):
        return self.__DSMBlockId
    def getDSMId(self):
        return self.__DSMId
    def getDSKPKS(self):
        return self.__DSKPKS
    def getDSKPKS(self):
        return self.__DSKPKS
    def getHkroot(self):
        return self.__hkroot
    def getMack(self):
        return self.__mack


class svConstellation(svNavMessage):
    def __init__(self,numSV):
        self.__sv = [[None,None] for i in range(numSV)]
        for i in range(numSV): 
            self.__sv[i][0] = i+1
            self.__sv[i][1] = svNavMessage()
    def getSvNavMessageObject(self, svId):
        return self.__sv[svId-1][1]
    def getSvDataSubFrame(self, svId):
        return self.__sv[svId-1][1].getDataSubframe()
    def getSvOsnma(self, svId):
        return self.__sv[svId-1][1].getOsnmaSubFrame()
    def feedConstellation(self,svId=int,wordType=int,data=bitarray(),osnma=bitarray()):
        self.__sv[svId-1][1]
        

