import logging
from bitarray import bitarray
from bitarray.util import int2ba, ba2int, ba2hex
from math import ceil

NB_DK_dict = {1:7,2:8,3:9,4:10,5:11,6:12,7:13,8:14}
DSM_KROOT_LDK_dict = {1:728,2:823,3:936,4:1040,5:1144,6:1248,7:1352,8:1456}
HF_dict = {0:'sha256',2:'sha3256'}
MF_dict = {0:'sha256',1:'AES'}
KS_dict = {0:96, 1:104, 2:112, 3:120, 4:128, 5:160, 6:192, 7:224, 8:256}
TS_dict = {5:20, 6:24, 7:28, 8:32, 9:40}


def DSM_Getter(galCons, svId):
    # Function to support the easy extract of the different DSM Information
    from dataProcessingOsnma_svKrootOsnmaMack import osnmaSplitter
    osnmaDivider = osnmaSplitter()
    DataFrameTime = galCons.getSvGST(svId)
    OSNMA = galCons.getSvOsnmaOnGST(svId, DataFrameTime)
    
    osnmaDivider.osnmaSubFrame2hkRootMack(OSNMA)
    DSM_ID = osnmaDivider.getDSMId()
    DSM_BID = osnmaDivider.getDSMBlockId()
    DSM_Block = osnmaDivider.getDSMBlock()
    DSM_NMAS = osnmaDivider.getNMAS()
    DSM_CID = osnmaDivider.getCID()
    DSM_CDPKS =osnmaDivider.getCDPKS()
    NMAHeader = osnmaDivider.getNMAHeader()
    return DSM_ID, DSM_BID, DSM_Block, DSM_NMAS, DSM_CID, DSM_CDPKS, NMAHeader


def concatenateBytes(iputBytelist):
    from bitarray import bitarray
    outputlist = ""
    for item in iputBytelist:
        b = bitarray()
        b.frombytes(item)
        outputlist += b.to01()
    b = bitarray(outputlist)
    return b.tobytes()

class DSMMessage: #Class to store the DSM Message (from several Space Vehicles)
    #id is the DSM_ID (first 4 bits of the DSM ID)
    # index is the DSM Block ID
    def __init__(self,ID):
        self.__dsm_blocks = [None for i in range(16)]# up to 14 Blocks as per section 3.2.3.1
        self.__dsm_type = "DSM-HKROOT" # to be changed when DSM-PKR is to be implemented
        self.__num_blocks = None
        self.__curr_blocks = 0
        self.__DSM_Id = ID
        self.__alreadyLogged  = False
    def getDSMId(self):
        return self.__DSM_Id
    def getDSMType(self):
        return self.__dsm_type
    def getNumBlocks(self):
        return self.__num_blocks
    def getCurrBlocks(self):
        return self.__curr_blocks
    def addBlock(self, index, block):
        if self.__dsm_blocks[index] == None:
            self.__curr_blocks += 1
            self.__dsm_blocks[index] = block
            logging.info("DSM#"+str(self.__DSM_Id)+" Received Block# "+str(index))
        if index == 0:
            b = bitarray()
            b.frombytes(block)
            c = ba2int(b[:4])
            if 0 < c < 8:
                self.__num_blocks = NB_DK_dict[c]
                self.__ldk = DSM_KROOT_LDK_dict[c]
                logging.info("DSM#"+str(self.__DSM_Id)+" has a total of "+str(self.__num_blocks)+" blocks")
            else: logging.info("DSM#"+str(self.__DSM_Id)+"cannot be added as it is a Reserved block")
        if self.isComplete():
            if self.__alreadyLogged == False:
                logging.info("DSM#"+str(self.__DSM_Id)+" is complete")
                self.__alreadyLogged = True
            blocks_bytes = self.__dsm_blocks[0:self.__num_blocks ]
            blocks_bytes = concatenateBytes(blocks_bytes)
            b = bitarray()
            b.frombytes(blocks_bytes)
            self.getParameters(b)
    def setDSM(self, b): # For testing purposes, as the test vector is per DSM complete and not blocks
            self.getParameters(b)
    def getParameters(self, b):
            c = ba2int(b[:4])
            self.__num_blocks = NB_DK_dict[c]
            self.__ldk = DSM_KROOT_LDK_dict[c]
            self.__NBdk = b[0:4]
            self.__PKID = b[4:8]
            self.__CIDKR = b[8:10]
            self.__Reserved1 = b[10:12]
            self.__hfBin = b[12:14]
            self.__mfBin = b[14:16]
            self.__lkBin = b[16:20]
            self.__tsBin = b[20:24]
            self.__hf = HF_dict[ba2int(b[12:14])]
            self.__mf = MF_dict[ba2int(b[14:16])]
            self.__lk = KS_dict[ba2int(b[16:20])]
            self.__ts = TS_dict[ba2int(b[20:24])]
            self.__mactl = b[24:32]
            self.__Reserved = (b[32:36])
            self.__WNk = (b[36:48])
            self.__TOWk = (b[48:56])
            self.__alpha = (b[56:104])
            self.__kroot = (b[104:104+self.__lk])
            oper = int(len(b)/104)
            self.__lds = 0
            diff = 1
            while diff != 0: # Iterative process to get the lenfth of the Digital Signature
                diff = int(len(b)) - 104*ceil(1+(self.__lk+self.__lds)/104)
                self.__lds += 8 #long has to be a byte-multiple
            self.__ds = (b[104+self.__lk:104+self.__lk+self.__lds])
            self.__Pdk = (b[104+self.__lk+self.__lds:len(b)])
    def isComplete(self):
        if self.__num_blocks != None:
            if (16 - self.__dsm_blocks.count(None)) == self.__num_blocks:
                return True
        return False
    def getM(self,NMAS):
        self.__M = NMAS + self.__CIDKR + self.__Reserved1 + self.__hfBin + self.__mfBin +self.__lkBin+ self.__tsBin + self.__mactl + self.__Reserved + self.__WNk + self.__TOWk + self.__alpha + self.__kroot
        return (self.__M).tobytes()
    def getKroot(self):
        return (self.__kroot).tobytes()
    def getKrootTime(self):
        return self.__WNk + self.__TOWk
    def getKrootTimeSeconds(self):
        return ba2int(self.getWNk())*7*24*3600+ba2int(self.getTOWHk())*3600
    def getKrootSize(self):
        return self.__lk
    def getTagSize(self):
        return self.__ts
    def getAlpha(self):
        return self.__alpha
    def getPkid(self):
        return self.__PKID
    def getWNk(self):
        return self.__WNk
    def getTOWHk(self):
        return self.__TOWk
    def getTagSize(self):
        return self.__ts
    def getMACTL(self):
        return self.__mactl
    def getReseved(self):
        return self.__Reserved
    def getDS(self):
        return (self.__ds).tobytes()
    def getPdk(self):
        return self.__Pdk
    def getCIDKR(self):
        return self.__CIDKR
    
