from bitarray import bitarray
from bitarray.util import int2ba, ba2int
word_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]


class svNavMessage:
    def __init__(self):
        self.__page_position = 0
        self.__data_subframe = [None for i in range(15)]
        self.__data_dataFrame = [] #As I/NAV message is composed of 24 sub-Frames, it is planned to add constraints here to have up to 24 frames
        self.__onsma_dataFrame = []
        self.__osnma_subframe = [None for i in range(15)]
        self.__pageDummy = False
        self.__dataFrameCompleteStatus = False
        self.__OsnmaDistributionStatus = False
        self.__wordType = bitarray()
    def subFrameSequence(self,wordType=int,data=bitarray(),osnma=bitarray()):
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
                else: #In Sync Complete
                    self.__page_position = 0
                    self.__dataFrameCompleteStatus = True
                if wordType == 5:
    
                    b = bitarray()
                    b.frombytes(data)
                    GST_current_WN = b[0:12]
                    GST_current_TOW = b[85:105]
                    self.__naturalTime = self.weekSeconds2Time(ba2int(GST_current_TOW))
                    GST_t0_TOW = ba2int(GST_current_TOW)-25 
                    self.__t0Time = self.weekSeconds2Time(GST_t0_TOW)
                    print(self.__naturalTime)
                    print(self.__t0Time)
                    
            else:
                self.__page_position = 0 #OUT OF SYNC
                self.__dataFrameCompleteStatus = False
                
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
