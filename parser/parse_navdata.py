import csv


word_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]



class sv_data:
    def __init__(self,sv_id,word_type=0,data=None,reserved1=None):
        self.__sv_id = sv_id
        self.__page_position = 0
        self.__data_subframe = [None for i in range(15)]
        self.__osnma_subframe = [None for i in range(15)]
        self.__pageDummy = False
        self.__dataFrameCompleteStatus = False
    def getSVId(self):
        return self.__sv_id
    def getPagePosition(self):
        return self.__page_position
    def getDataFrameCompleteStatus(self):
        return self.__dataFrameCompleteStatus
    def getdataSubframe(self):
        return self.__data_subframe
    def sequence(self,word_type,data,reserved1):
        if int(word_type,2) == 63:  
            self.__pageDummy = True #Word Type as value 11111 (or 63) is considered as dummmy Page
            self.__dataFrameCompleteStatus = False
        else:
            self.__pageDummy = False
            if int(word_type,2) in word_types_sequence[self.__page_position]:
                self.__data_subframe[self.__page_position]=data
                self.__page_position = self.__page_position+1
                if self.__page_position == len(word_types_sequence):
                    self.__dataFrameCompleteStatus = True
                    self.__page_position = 0
                else: self.__dataFrameCompleteStatus = False
            else:
                self.__page_position = 0
                self.__data_subframe = [None for i in range(15)]
                self.__dataFrameCompleteStatus = False


sv_vector = [None for i in range(36)] #Current Issue of Galileo OS ICD states that SV (satellites) are up to 36

for i in range(36):
    sv_vector[i] = sv_data(i)
sv_vector[1].getPagePosition()
previousdata = ""
timestamp_av = False
repeated = True
dataold = ""
with open('../data2.csv') as csvfile:
        parsed_data = csv.reader(csvfile, delimiter=',')
        first = True
        
        for row in parsed_data:
            if first:
                first=False
                continue
            if timestamp_av:
                timestamp=str(row[0])
                sv_id=int(row[2])
                word1=int(row[9])
                word2=int(row[10])
                word3=int(row[11])
                word4=int(row[12])
                word5=int(row[13])
                word6=int(row[14])
                word7=int(row[15])
                word8=int(row[16])
            else:
                sv_id=int(row[2-1])
                word1=int(row[9-1])
                word2=int(row[10-1])
                word3=int(row[11-1])
                word4=int(row[12-1])
                word5=int(row[13-1])
                word6=int(row[14-1])
                word7=int(row[15-1])
                word8=int(row[16-1])
            data_k_word = bin((word1 & 0x3F000000) >> 24)[2:].zfill(6) #as per uBlox ICD, it is the same as I/NAV Word types
            #Even Page
            odd_even_0 = (word1 & 0x80000000) >> 31 # Always shuld be 0
            page_type_0 = (word1 & 0x40000000) >> 30 # In Nominal, 0
            data_k_1 = bin((word1 & 0xFFFFFF))[2:].zfill(24) #Data k as per Galileo ICD (not inlcluding word type, first 6 bits)
            data_k_2 = bin(word2)[2:].zfill(32)
            data_k_3 = bin(word3)[2:].zfill(32)
            data_k_4 = bin((word4 & 0xFFFFC000) >> 14)[2:].zfill(18)
            data_k = data_k_word + data_k_1 + data_k_2 + data_k_3 + data_k_4 # Full data_k of Galileo OS ICD
            tail = bin((word4 & 0x3F00) >> 8)[2:].zfill(6)
            
            #Odd Page
            odd_even_1 = (word5 & 0x80000000) >> 31 # Always should be 1
            page_type_1 = (word5 & 0x40000000) >> 30 # In Nominal, 0
            data_j = bin((word5  & 0x3FFFC000)>>14)[2:].zfill(16)
            res1_1 = bin((word5 & 0x3FFF))[2:].zfill(14)
            res1_2 = bin((word6 & 0xFFFFFFC0) >> 6)[2:].zfill(26)
            reserved_1 = res1_1+res1_2
            sar_1 = bin(word6 & 0x3F)[2:].zfill(6) 
            sar_2 = bin((word7 & 0xFFFF0000) >> 16)[2:].zfill(16)
            sar = sar_1 + sar_2
            spare = bin((word7 & 0xC000) >> 14)[2:].zfill(2)
            crc_1 = bin((word7 & 0x3FFF))[2:].zfill(14)
            crc_2 = bin((word8 & 0xFFC00000) >> 24)[2:].zfill(10)
            crc = crc_1 + crc_2
            res2 = bin((word8 & 0x3FC000) >> 14)[2:].zfill(8)
            tail = bin((word8 & 0x3F00) >> 8)[2:].zfill(6)
            #Total Info
            data = data_k + data_j
            data_noword = data_k_1 + data_k_2 + data_k_3 + data_k_4 + data_j
            if data == dataold:
                repeated = True
            else:
                dataold = data
                repeated = False
            #print(int(data_k_word,2))
            if not repeated:
                sv_vector[sv_id].sequence(data_k_word,data, reserved_1)
                if sv_vector[sv_id].getDataFrameCompleteStatus():
                    print("SVID: ",sv_vector[sv_id].getSVId(), "Sub-Frame Completed Status:", sv_vector[sv_id].getDataFrameCompleteStatus())
