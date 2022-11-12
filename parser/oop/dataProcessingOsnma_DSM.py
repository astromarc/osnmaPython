import logging
from dataProcessingSupport import concatenateBytes
from bitarray import bitarray
from bitarray.util import int2ba, ba2int, ba2hex
from math import ceil

NB_DK_dict = {1:7,2:8,3:9,4:10,5:11,6:12,7:13,8:14}
DSM_KROOT_LDK_dict = {1:728,2:823,3:936,4:1040,5:1144,6:1248,7:1352,8:1456}
HF_dict = {0:'sha256',2:'sha3256'}
MF_dict = {0:'sha256',1:'AES'}
KS_dict = {0:96, 1:104, 2:112, 3:120, 4:128, 5:160, 6:192, 7:224, 8:256}
TS_dict = {5:20, 6:24, 7:28, 8:32, 9:40}


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
            self.__num_blocks = NB_DK_dict[c]
            self.__ldk = DSM_KROOT_LDK_dict[c]
            logging.info("DSM#"+str(self.__DSM_Id)+" has a total of "+str(self.__num_blocks)+" blocks")
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
    
class keyChain:
    '''
    Class to check belonging of 
    '''
    def __init__(self, hkroot, hkrootTime, hkrootTimeSeconds, alpha, keyLength):
        self.__hkroot = hkroot
        self.__alpha = alpha
        self.__hkrootTime = hkrootTime
        self.__hkrootTimeSeconds = hkrootTimeSeconds
        self.__keyLength = keyLength
        self.__currentComputedRootKey = None
        logging.info("HKROOT decoded: "+str((self.__hkroot).hex()))
    def setLastTeslaKey(self, lastTeslaKey, lastTimeSeconds):
        self.__lastTeslaKey = lastTeslaKey
        self.__lastTimeSeconds = lastTimeSeconds
    def checkRootKeyValidity(self):
        pass
    def checkTeslaKeyAgainsRootKey(self, teslaKey, teslaKeyTime, teslaKeyTimeSeconds):
        from dataProcessingSupport import computeDelayedTime
        self.__lastTeslaKey = teslaKey
        numIter = ((teslaKeyTimeSeconds-self.__hkrootTimeSeconds)/30)+1
        itera = 0
        while itera < numIter:
            computeDelaytimePreviousKey = computeDelayedTime(teslaKeyTime,30)
            previousTeslaKey = self.computedDelayedKey(teslaKey, computeDelaytimePreviousKey)
            teslaKeyTime = computeDelaytimePreviousKey
            teslaKey = previousTeslaKey
            itera = itera+1
        self.__currentComputedRootKey = teslaKey
        if teslaKey == self.__hkroot: 
            logging.info("Tesla Key: "+ str((self.__lastTeslaKey).hex())+ " belongs to a chain with root "+ str((self.__hkroot.hex()))) 
            return True
        else:
            logging.warn("Tesla Key: "+ str((self.__lastTeslaKey).hex())+ " cannot be verified against root key "+ str((self.__hkroot.hex()))) 
            return False
    def computedDelayedKey(self,key,time):
        from bitarray import bitarray
        from hashlib import sha256
        b = bitarray()
        c = bitarray()
        d = bitarray()
        d.frombytes(key)
        b.frombytes(self.__alpha)
        c.frombytes(time)
        value = d + c + b
        e = bitarray()
        value = value.tobytes()
        value = sha256(value).digest()
        e.frombytes(value)
        e = e[0:self.__keyLength]
        return e.tobytes()
    def getCurrentComputedTeslaKey(self):
        return self.__currentComputedRootKey
