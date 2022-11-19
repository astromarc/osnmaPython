from bitarray import bitarray
from bitarray.util import int2ba, ba2int, ba2hex, hex2ba
from dataProcessingOsnma_svKrootOsnmaMack import osnmaSplitter, mackParser
import hmac
import hashlib
from hashlib import sha256
import logging
import ecdsa
import re

osnmaDivider = osnmaSplitter()
mackDivider = mackParser()

def computeDelayedTime (GST_T0,delay):
    #it assumes that a delay positive means you want to get an "earlier" time
    #e.g., time 14:30 and delay 30 will return 14:00, whilst delay -30 will return 15:00
    from bitarray import bitarray
    from bitarray.util import int2ba, ba2int
    b = bitarray()
    b.frombytes(GST_T0)
    b_WN = b[0:12]
    b_TOW = b[12:]
    if delay >=0:
        i_WN = ba2int(b_WN)
        i_TOW = ba2int(b_TOW) - delay
        if i_TOW < 0:
            i_WN = i_WN - 1
            i_TOW = 7*24*3600 - i_TOW

    if delay <0:
        i_WN = ba2int(b_WN)
        i_TOW = ba2int(b_TOW) - delay
        if i_TOW> 604799:
            i_WN = i_WN + 1
            i_TOW = 604799 - (604799+delay+30)

    b_WN = int2ba(i_WN,12)
    b_TOW = int2ba(i_TOW,20)
    osnmaTime = b_WN+b_TOW
    return osnmaTime.tobytes()


def navData(subFrame, ADKD=0): #if no value is indicated it is assumed ADKD = 0
    from bitarray import bitarray
    from bitarray.util import ba2int
    word = bitarray()
    b = bitarray()
    if ADKD == 0 or ADKD == 12:
        b.frombytes(subFrame[10])
        word1_num = b[0:6]
        word1 = b[6:126]  
        
        b = bitarray()
        b.frombytes(subFrame[0])
        word2_num = b[0:6]
        word2 = b[6:126]
        
        b = bitarray()
        b.frombytes(subFrame[11])
        word3_num = b[0:6]
        word3 = b[6:]

        b = bitarray()
        b.frombytes(subFrame[1])
        word4_num = b[0:6]
        word4 = b[6:126]

        b = bitarray()
        b.frombytes(subFrame[12])
        word5_num = b[0:6]
        word5 = b[6:128-(23+12+20)]
        
        word = word1 + word2 + word3 + word4 + word5
        
        return word
        
    if ADKD == 4:
        b = bitarray()
        b.frombytes(subFrame[2])
        word1_num = b[0:6]
        word1 = b[6:len(b)-3]
        
        b = bitarray()
        b.frombytes(subFrame[4])
        word2_num = b[0:6]
        word2 = b[-42:]
        
        word = word1 + word2
        
        if ba2int(word2_num) == 10: # as in position number 5 we can have wether an 8 or a 10. If it is 8, we return a False.
            return word
        else: return False

class checkRootKey:
    def checkRootKeyValidity(filename,message,sig):
        with open(filename, 'r') as f:
            pemFile = f.read().replace('\n', '')
        pattern = '-----BEGIN PUBLIC KEY-----(.*?)-----END PUBLIC KEY-----'
        pem_sring = re.search(pattern, pemFile).group(1)
        key = ecdsa.VerifyingKey.from_pem(pem_sring, hashfunc = hashlib.sha256)
        try:
            key.verify(sig, message)
            logging.info("Digital Signature "+sig.hex()+" verified against GSC Public Key "+pem_sring)
            return True
        except: 
            logging.warn("Digital Signature "+sig.hex()+" cannot be verified against GSC Public Key "+pem_sring)
            return False

class NavDataAuthenticator:
    
    '''
    This class implements the functionality purely related to the Authentication of the Space Vehicles.
    As a main methods, it has:
        - computeSelfAuthentication: This method is in charge of computing the Self-Authentication.
            As an output, it returns:
                0: the SV is Self-Authenticated
                1: the SV Self-Authentication has failed.
                2: the SV cannot be self-authenticated as it is missing the delayed Navigation Data.
        - computeCrossAuthentication: this method is in charge of computing the Cross-Authentication. It calls different methods depending on the Cross-Authentication ADKD.
        - getCrossAuthentication: it returns a list with the cross-authentication status associated with it's corresponding PRND. It returns a list of items with two elements: the PRND and the Cross-Authentication Status (which follows the same output types as per Self-Authentication)
    '''
    def __init__(self):
        self.__SelfAuthStatus = False
        self.__CTR = 2
        self.__key = None
        self.__osnmaData = None
    def getSelfAuthentication(self,timeBytes,svId,svDataFrame,svOsnmaFrame,keyLength,tagLength, DSM_NMAS):
        '''
        This method us used to return the Self-Authenciation of a certain Space Vehicle.
        As an input, it gets:
            - timeBytes: current SubFrame GST0 time in a Bytes format
            - OSNMA Frame: List of OSNMA SubFrames. Each Subframe is indexed by a GST0 (in bytes).
            - NavData Frame: List of Navifation Data Subframe. Each Subframe is indexed by a GST0 (in bytes).
            - svId: integer indicating the svID.
            - keyLength: Length of the Tesla Key, in integer format.
            - tagLength: Length of the Tags, in integer format.
        This method returns a boolean value:
            -0 if Space Vehicle is Self-Authenticated
            -1 if Space Vehicle is not Self-Authenticated because Tag0 comparison fails
            -2 if there is no enough info to compute the Self-Authentication
        '''
        
        timeDelayed30Bytes = computeDelayedTime(timeBytes,30)
        timeDelayed60Bytes = computeDelayedTime(timeBytes,60)
        
        timeBits = bitarray()
        timeDelayed30Bits = bitarray()
        timeDelayed60Bits = bitarray()
        
        timeBits.frombytes(timeBytes)
        timeDelayed30Bits.frombytes(timeDelayed30Bytes)
        timeDelayed60Bits.frombytes(timeDelayed60Bytes)
        
        navDataBytesDelayed = [None]
        for  item in svDataFrame:
            if (item[1] == timeDelayed60Bytes):
                navDataBytesDelayed = item[2]
        osnmaDataDelayedBytes = [None]
        for  item in svOsnmaFrame:
            if (item[1] == timeDelayed30Bytes):
                    osnmaDataDelayedBytes = item[2]
                
        osnmaDataBytes = [None]
        for  item in svOsnmaFrame:
            if (item[1] == timeBytes):
                osnmaDataBytes = item[2]
        
        if not any(item is  None for item in navDataBytesDelayed) and not any(item is  None for item in osnmaDataDelayedBytes)  and not any(item is  None for item in osnmaDataBytes) and not  any(item == b'\x00\x00\x00\x00\x00' for item in osnmaDataDelayedBytes):
        ### Getting the Tesla Key (GTS0)
            osnmaDivider.osnmaSubFrame2hkRootMack(osnmaDataBytes)
            mackDivider.parseMackMessage(osnmaDivider.getMack(), keyLength, tagLength)
            key = mackDivider.getTeslaKey()
            
        ### Getting the Tag0 (GST0-30seconds)
            osnmaDivider.osnmaSubFrame2hkRootMack(osnmaDataDelayedBytes)
            mackDivider.parseMackMessage(osnmaDivider.getMack(), keyLength, tagLength)
            tag0 = mackDivider.getTag0()
            
            
        ### Getting the Message "m" (GST0-60seconds)
            NMAS = int2ba(DSM_NMAS,2)
            PRNA = int2ba(svId,8)
            CTR = int2ba(1,8) # CTR is fixed at int 1 for Self-Authentication.
            ADKD0_NavData = navData(navDataBytesDelayed)
            m = PRNA+timeDelayed30Bits+CTR+NMAS+ADKD0_NavData
            m.fill()
            
        ### Comparing tag0 and hashed (with key) message m 
            h = bitarray()
            h.frombytes(hmac.digest(key, m.tobytes(), 'sha256'))
            h = h[:40]
            
            if h.tobytes() == tag0: 
                logging.info("SV"+str(svId)+" is Self-Authenticated")
                return 0
            else:
                logging.info("SV"+str(svId)+" is not Self-Authenticated. Computed tag: "+str(ba2hex(h))+" ; expected tag "+str(tag0.hex()))
                return 1
            
        else:
            if navDataBytesDelayed == None:
                logging.info("SV"+str(svId)+" cannot perform Self-Authentication as it is missing the Delayed Navigation Data ")
            else:
                logging.info("SV"+str(svId)+" cannot perform Self-Authentication as it is missing the delayed Tag0 ")
            return 2
    def computeCrossAuthentication(self, svId,  timeBytes,svOsnmaFrame,keyLength,tagLength, DSM_NMAS, galCons):
            '''
            Cross-Authentication method
            Please note that in case PRND = 255 this is a special case which is also Self-Authentication 
            svId is the key currently transmitting the Key and the Tags
            '''
            timeDelayed30Bytes = computeDelayedTime(timeBytes, 30)
            timeDelayed60Bytes = computeDelayedTime(timeBytes, 60)
            timeDelayed30Bits = bitarray()
            timeDelayed30Bits.frombytes(timeDelayed30Bytes)
            self.__crossAuthenticationStatus =[]
            self.__sv_id = svId
            # In all cases (ADKD 12, 4 or 0) Tesla Key is the key from the currently transmitted Sub-Frame
            osnmaData = galCons.getSvOsnmaOnGST(svId, timeBytes)
            if osnmaData is not None:
                osnmaDivider.osnmaSubFrame2hkRootMack(osnmaData)
                mackDivider.parseMackMessage(osnmaDivider.getMack(), keyLength, tagLength)
                self.__key = mackDivider.getTeslaKey()
                self.__osnmaData = osnmaData
                self.__crossAuthenticationStatus.append(self.computeCrossAuthentication_ADKD12(svId, timeBytes, keyLength, tagLength, DSM_NMAS, galCons))
                # Getting the Tags
                osnma30Delayed   = galCons.getSvOsnmaOnGST(svId, timeDelayed30Bytes)
                if osnma30Delayed is not None:
                    osnmaDivider.osnmaSubFrame2hkRootMack(osnma30Delayed)
                    mackDivider.parseMackMessage(osnmaDivider.getMack(), keyLength, tagLength)
                    self.__CTR = 2
                    for item in mackDivider.getTagsAndInfo():
                        if  item['PRND'] == 255: # In this particular case, it is like self-authentication
                            PRND = svId
                            crossAuthStatus = self.computeCrossAuthentication_PRND255(PRND, timeBytes,tagLength, DSM_NMAS, galCons, item['Tag'])
                            self.__crossAuthenticationStatus.append([255,crossAuthStatus])
                        else: # actual Cross-Authentications
                            if item['ADKD'] == 4 or item['ADKD'] == 0: # Currently, ADKD4 only applies to PRND = 255; however the method is kept flexible for ADKD4 or ADKD0 for future Cross-Authentication
                                crossAuthStatus = self.computeCrossAuthentication_ADKD0_4(item['PRND'], svId, timeBytes, tagLength, DSM_NMAS, galCons, item['ADKD'], item['Tag'])
                                self.__crossAuthenticationStatus.append([item['PRND'],crossAuthStatus])
                        self.__CTR+=1
                else: 
                    return 2
                #ADKD12
                
            else: 
                logging.info("SV"+str(svId)+" cannot perform Self-Authentication as it is missing the delayed Tag0 ")
                return 2
    
    
    def computeCrossAuthentication_ADKD12(self,svId, timeBytes,keyLength,tagLength,DSM_NMAS, galCons):
        timeDelayed300Bytes = computeDelayedTime(timeBytes, 330)
        timeDelayed330Bytes = computeDelayedTime(timeBytes, 360)
        timeDelayed300Bits = bitarray()
        timeDelayed300Bits.frombytes(timeDelayed300Bytes)
        #1st getting the Tags from the delayed tags
        osnma300Delayed = galCons.getSvOsnmaOnGST(svId, timeDelayed300Bytes)
        if osnma300Delayed is not None:
            CTR = 2
            osnmaDivider.osnmaSubFrame2hkRootMack(osnma300Delayed)
            mackDivider.parseMackMessage(osnmaDivider.getMack(), keyLength, tagLength)
            for item in mackDivider.getTagsAndInfo():
                if item['ADKD'] == 12:
                    navData330Delayed = galCons.getSvDataOnGST(item['PRND'], timeDelayed330Bytes)
                    if navData330Delayed is not None:
                        PRNA = int2ba(svId,8)
                        PRND = int2ba(item['PRND'],8)
                        CTRi = int2ba(CTR,8)
                        NMAS = int2ba(DSM_NMAS,2)
                        navDataADKD12 = navData(navData330Delayed,12)
                        m = PRND+PRNA+timeDelayed300Bits+CTRi+NMAS+navDataADKD12
                        m.fill()
                        h = bitarray()
                        h.frombytes(hmac.digest(self.__key, m, 'sha256'))
                        h = h[:tagLength]
                        if item['Tag'] == h.tobytes():
                            logging.info("SV"+str(self.__sv_id)+" has successfully Cross-Authenticated ADKD12 NavData from SV "+str(item['PRND']))
                            return [item['PRND'],0]
                        else:
                            logging.warn("SV"+str(self.__sv_id)+" failed when Cross-Authenticating ADKD12 NavData from SV "+str(item['PRND']))
                            return [item['PRND'],1]
                    else:
                        logging.info("SV"+str(self.__sv_id)+" cannot Cross-Authenticate ADKD12 NavData from SV"+str(item['PRND'])+" due to lack of Navigation Data")
                        return [item['PRND'],2]
                CTR+=1
        else:
            logging.info("SV"+str(self.__sv_id)+" cannot authenticate ADKD12 NavData due to lack of Tags")
            #return [item['PRND'],2]
        
    def computeCrossAuthentication_ADKD0_4(self,PRND,svId, timeBytes,tagLength,DSM_NMAS, galCons, ADKD, tag):
        
        timeDelayed60Bytes = computeDelayedTime(timeBytes, 60)
        timeDelayed30Bytes = computeDelayedTime(timeBytes, 30)
        timeDelayed30Bits = bitarray()
        timeDelayed30Bits.frombytes(timeDelayed30Bytes)
        navData60Delayed = galCons.getSvDataOnGST(PRND, timeDelayed60Bytes)
        PRNDlog = PRND
        if navData60Delayed is not None:
            PRNA = int2ba(svId,8)
            PRND = int2ba(PRND,8)
            CTRi = int2ba(self.__CTR,8)
            NMAS = int2ba(DSM_NMAS,2)
            navDataADKD4 = navData(navData60Delayed,ADKD)
            m = PRND+PRNA+timeDelayed30Bits+CTRi+NMAS+navDataADKD4
            m.fill()
            h = bitarray()
            h.frombytes(hmac.digest(self.__key, m, 'sha256'))
            h = h[:tagLength]
            if h.tobytes() == tag:
                logging.info("SV"+str(self.__sv_id)+" has successfully Cross-Authenticated ADKD"+str(ADKD)+ " NavData from SV "+str(PRNDlog))
                return 0
            else:
                logging.warn("SV"+str(self.__sv_id)+" failed when Cross-Authenticating ADKD"+str(ADKD)+" NavData from SV "+str(PRNDlog))
                return 1
        else:
            logging.info("SV"+str(self.__sv_id)+" cannot authenticate ADKD"+str(ADKD)+ " NavData from SV "+str(PRNDlog)+" due to the lack of navigation data")
            return 2
            
    def computeCrossAuthentication_PRND255(self,PRND,timeBytes,tagLength,DSM_NMAS, galCons,tag):
        
        timeDelayed60Bytes = computeDelayedTime(timeBytes, 60)
        timeDelayed30Bytes = computeDelayedTime(timeBytes, 30)
        timeDelayed30Bits = bitarray()
        timeDelayed30Bits.frombytes(timeDelayed30Bytes)
        
        navData60Delayed = galCons.getSvDataOnGST(PRND, timeDelayed60Bytes)
        if navData60Delayed is not None: 
            navDataADKD4 = navData(navData60Delayed,4)
        if navData60Delayed is not None and navDataADKD4 is not False:
            CTRi = int2ba(self.__CTR,8)
            PRND = int2ba(PRND,8)
            NMAS = int2ba(DSM_NMAS,2)
            m = PRND+PRND+timeDelayed30Bits+CTRi+NMAS+navDataADKD4
            m.fill()
            h = bitarray()
            h.frombytes(hmac.digest(self.__key, m, 'sha256'))
            h = h[:tagLength]
            if h.tobytes() == tag:
                logging.info("SV"+str(self.__sv_id)+" is Self-Autenticated with PRN 255")
                return 0
            else: 
                logging.warn("SV"+str(self.__sv_id)+" failed when Authenticating with PRN 255")
                return 1
        else: 
            logging.info("SV"+str(self.__sv_id)+" cannot be Self-Autenticated with PRN255 (ADKD4) due to lack of Navigation Data")
            return 2
        
    def getCrossAuthenticationStatus(self):
        return self.__crossAuthenticationStatus
    
    
class keyChain:
    '''
    Class to check belonging of a Tesla Key of a HKROOT
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
    def checkTeslaKeyAgainsRootKey(self, teslaKey, teslaKeyTime, teslaKeyTimeSeconds):

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
    

