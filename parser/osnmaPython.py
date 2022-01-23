word_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]
Nbdk_lookup = [None, 728, 832, 936, 1040, 1144, 1248, 1352, 1456, None, None, None, None, None, None, None]
HF_lookup = ["SHA-256", None, "SHA3-256", None]
MF_lookup = ["HMAC-SHA-256", "CMAC-AES", None, None]
KS_lookup = [96, 104, 112, 120, 128, 160, 192, 224, 256, None, None, None, None, None, None, None]
TS_lookup = [None, None, None, None, None, 20, 24, 28, 32, 40, None, None, None, None, None, None]


# Class to store info of all the defined Galileo SiS ICD Data (per Space Vehicle)
class sv_data:
    def __init__(self,sv_id,word_type=0,data=None,reserved1=None):
        self.__sv_id = sv_id
        self.__page_position = 0
        self.__data_subframe = [None for i in range(15)]
        self.__data_subframe_hist = [] #As I/NAV message is composed of 24 sub-Frames, it is planned to add constraints here to have up to 24 frames
        self.__osnma_subframe = [None for i in range(15)]
        self.__pageDummy = False
        self.__dataFrameCompleteStatus = False
    def getSVId(self):
        return self.__sv_id
    def getPagePosition(self):
        return self.__page_position
    def getDataFrameCompleteStatus(self):
        return self.__dataFrameCompleteStatus
    def getDataSubframe(self):
        return self.__data_subframe
    def getDataFrame(self):
            return self.__data_subframe_hist
    def getOsnmaSubframe(self):
            return self.__data_subframe
    def subFrameSequence(self,word_type,data,reserved1): #As pages follow a pre-defined order, we only consider we have a complete sub-frame if we get the 15 pages (even+odd pages)
        if int(word_type,2) == 63:  
            self.__pageDummy = True #Word Type as value 11111 (or 63) is considered as dummmy Page
            self.__dataFrameCompleteStatus = False
        else:
            self.__pageDummy = False
            if int(word_type,2) in word_types_sequence[self.__page_position]:
                self.__data_subframe[self.__page_position]=data
                self.__osnma_subframe[self.__page_position]=reserved1
                self.__page_position = self.__page_position+1
                if self.__page_position == len(word_types_sequence):
                    self.__dataFrameCompleteStatus = True
                    self.__page_position = 0
                    self.__data_subframe_hist.append(self.__data_subframe)
                else: self.__dataFrameCompleteStatus = False
            else:
                self.__page_position = 0
                self.__data_subframe = [None for i in range(15)]
                self.__osnma_subframe= [None for i in range(15)]
                self.__dataFrameCompleteStatus = False

#This class takes as an input a list of a complete sub-frame OSNMA (in integer format) and has a method to ouputs:
# list of MACKs, HKROOT, NMEA Header (with all its values (NMAS, CID, CPKS, Reserved))
# DSM Header (With DSM ID and DSM Block ID)
# It assumes the list of osnma's words is sorted 
class osnma:
    def __init__(self,input_osnma_list):
        osnma_list = input_osnma_list
        #for osnma_word in osnma_list:
        #    hkRoot_word = 

class DSMMessage: #Class to store the DSM Message (from several Space Vehicles)
    def __init__(self, id):
        self.__dsm_id = id 
        self.__dsm_blocks = [None for i in range(16)]
        self.__dsm_type = "DSM-PKR"
        self.__num_blocks = None
        self.__curr_blocks = 0
        if id <= 11:
            self.__dsm_type = "DSM-KROOT"
    def getDSMId(self):
        return self.__dsm_id
    def getDSMType(self):
        return self.__dsm_type
    def getNumBlocks(self):
        return self.__num_blocks
    def getCurrBlocks(self):
        return self.__curr_blocks
    def addBlock(self, index, block):
        assert (index < 16)
        self.__dsm_blocks[index] = block
        if index == 0:
            self.__num_blocks = ((block[0] & 0xF0) >> 4) + 6
        if not self.isComplete():
            self.__curr_blocks += 1
    def isComplete(self):
        if self.__num_blocks != None:
            if (16 - self.__dsm_blocks.count(None)) == self.__num_blocks:
                return True
        return False
    def getDSMBytes(self):
        if self.isComplete():
            return [b for block in self.__dsm_blocks[:self.__num_blocks] for b in block]
        return None
    def __repr__(self):
        return self.__dsm_type + " (Type: " + str(self.__dsm_id) + ") " + "Num blocks: " + str(self.__num_blocks) + " Blocks: " + str(self.__dsm_blocks)

def getUbloxData(record = False,filename='galileoTest.csv',COMPort='COM19'):
    # This function takes as an input:

    from serial import Serial
    from pyubx2 import UBXReader
    import csv
    
    ubxPages = []
    ubxPages_new = []
    
    stream = Serial(COMPort, 9600, bytesize=8, parity='N', stopbits=1,)
    ubr = UBXReader(stream)
    (raw_data, parsed_data) = ubr.read()
    if parsed_data is not None:
        ubxPages_new = str(parsed_data).split(",")
    stream.close()
    for x in ubxPages_new:
        if x != "<UBX(RXM-SFRBX":
            ubxSplit = x.split('=')[1].split(")")[0]
            ubxPages.append(ubxSplit)
    if record:
        with open(filename, 'a', newline='') as f:
            write = csv.writer(f)
            write.writerow(ubxPages)
            f.close()
    return ubxPages

def ubloxData2GalileoICD(ubxPages):
    #This Function takes as an input a ubxPages (list with values direclty extracted from uBlox Receiver)
    #and as an output it returns the I/NAV Galileo Pages (event and odd pages information)
    sv_id=int(ubxPages[1])
    word1=int(ubxPages[8])
    word2=int(ubxPages[9])
    word3=int(ubxPages[10])
    word4=int(ubxPages[11])
    word5=int(ubxPages[12])
    word6=int(ubxPages[13])
    word7=int(ubxPages[14])
    word8=int(ubxPages[15])
    
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
    return [sv_id, data_k_word, data, reserved_1]

def parse_nma_hdr(x):
    nmas_str = ["Reserved", "Test", "Operational", "Don't use"]
    cpks_str = ["Reserved", "Nominal", "End Of Chain (EOC)", "Chain Revoked (CREV)", "New Public Key (NPK)", "Public Key Revoked (PKREV)", "Reserved", "Reserved"]
    nmas = (x & 0xC0) >> 6
    chainID = (x & 0x30) >> 4
    cpks = (x & 0x0E) >> 1
    return "NMA HDR: " + nmas_str[nmas] + " | Chain ID: " + str(chainID) + " | CPKS: " + cpks_str[cpks]

def convert_mack_words_to_bytearray(words):
    last=0
    for i in words:
        last <<= 32
        last |= i
    return last

def parse_dsm_kroot_msg (msg):
    parsed_dsm_kroot = {}
    stream = msg.getDSMBytes()
    parsed_dsm_kroot["NBdk"] = Nbdk_lookup[(stream[0] & 0xF0) >> 4]
    parsed_dsm_kroot["PKID"] = stream[0] & 0x0F
    parsed_dsm_kroot["CIDKR"] = (stream[1] & 0xC0) >> 6
    parsed_dsm_kroot["Reserved1"] = (stream[1] & 0x30) >> 4
    parsed_dsm_kroot["HF"] = HF_lookup[(stream[1] & 0x0C) >> 2]
    parsed_dsm_kroot["MF"] = MF_lookup[stream[1] & 0x03]
    parsed_dsm_kroot["KS"] = KS_lookup[(stream[2] & 0xF0) >> 4]
    parsed_dsm_kroot["TS"] = TS_lookup[stream[2] & 0x0F]
    parsed_dsm_kroot["MACLT"] = stream[3]
    parsed_dsm_kroot["Reserved2"] = (stream[4] & 0xF0) >> 4
    parsed_dsm_kroot["WNk"] = ((stream[4] & 0x0F) << 8) |stream[5]
    parsed_dsm_kroot["TOWHk"] = stream[6]
    parsed_dsm_kroot["alfa"] = (stream[7] << 40) | (stream[8] << 32) | (stream[9] << 24) | (stream[10] << 16) | (stream[11] << 8) | stream[12]
    bytes_key = parsed_dsm_kroot["KS"] // 8
    parsed_dsm_kroot["KROOT"] = stream[13:13+bytes_key]
    parsed_dsm_kroot["DS+Padding"] = stream[13+bytes_key:]
    return parsed_dsm_kroot


def parse_dsm_pkr_msg (msg):
    parsed_dsm_pkr = {}

def unpack_mack_array(mack_array):
    arr = []
    for quad in mack_array:
        arr.append((quad & 0xFF000000) >> 24)
        arr.append((quad & 0x00FF0000) >> 16)
        arr.append((quad & 0x0000FF00) >> 8)
        arr.append(quad & 0x000000FF)
    return arr

def parse_mack_msg(msg, dsm_kroot):
    mbytes = unpack_mack_array(msg)
    parsed_mack_msg = {}
    parsed_mack_msg["Tag0"] = bytearray(mbytes[0:5])  #Fixed to 40 bits (5 bytes) but should be variable depending on TS value in DSM-KROOT message
    parsed_mack_msg["MACSEQ"] = (mbytes[5] << 4) | (mbytes[6] & 0xF0) >> 4
    num_tags = floor((480-128)/(40+16)) # Key(128) and tag(40) sizes shall be extracted from DSM-KROOT
    tags_and_info = []
    next_index = 7
    for i in range(num_tags):
        ti = {}
        ti["Tag"] = bytearray(mbytes[next_index:next_index+5])
        ti["Tag-Info"] = mbytes[next_index+5:next_index+7]
        ti["PRN"] = ti["Tag-Info"][0]
        ti["ADKD"] = (ti["Tag-Info"][1] & 0xF0) >> 4
        tags_and_info.append(ti)
        next_index +=7
    parsed_mack_msg["TagsAndInfo"] = tags_and_info
    parsed_mack_msg["Key"] = bytearray(mbytes[next_index:next_index+16])
    return parsed_mack_msg