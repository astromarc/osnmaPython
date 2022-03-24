from bitarray import bitarray

word_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]

class svConstellation:
    def __init__(self,numSV):
        self.__sv = [[None,None] for i in range(numSV)]
        for i in range(numSV): 
            self.__sv[i][0] = i+1
            self.__sv[i][1] = svNavMessage()
    def getSvNavMessage(self, svId):
        return self.__sv[svId-1][1]

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
            if self.__page_position == (len(word_types_sequence)):
                self.__page_position = 0
                self.__dataFrameCompleteStatus = True
            if wordType in word_types_sequence[self.__page_position]:
                self.__data_subframe[self.__page_position]=data
                self.__osnma_subframe[self.__page_position]=osnma
                self.__page_position = self.__page_position+1
                self.__dataFrameCompleteStatus = False
                if wordType == 2:
                    if int.from_bytes(osnma, 'big') == 0: self.__OsnmaDistributionStatus = False
                    else: self.__OsnmaDistributionStatus = True
    def testecillo(self,num):
        self.__test = num
        return num