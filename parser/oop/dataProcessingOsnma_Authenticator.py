from bitarray import bitarray
from bitarray.util import int2ba, ba2int, ba2hex, hex2ba
from dataProcessingSupport import computeDelayedTime, navData
from dataProcessingGalileoFrame_svKrootOsnmaMack import osnmaSplitter, mackParser
import hmac
import logging
from dataProcessingSupport import  weekSeconds2Time

osnmaDivider = osnmaSplitter()
mackDivider = mackParser()

class NavDataAuthenticator:
    
    '''
    This class implements the functionality purely related to the Authentication of the Space Vehicles.
    As a main methods, it has:
        - computeSelfAuthentication: This method is in charge of computing the Self-Authentication.
            As an output, it returns:
                0: the SV is Self-Authenticated
                1: the SV Self-Authentication has failed.
                2: the SV cannot be self-authenticated as it is missing the delayed Navigation Data.
    '''
    def __init__(self):
        self.__SelfAuthStatus = False
        self.__CTR = 2
        self.__key = None
        self.__osnmaData = None
    def computeSelfAuthentication(self,timeBytes,svId,svDataFrame,svOsnmaFrame,keyLength,tagLength, DSM_NMAS):
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
            CTRi = int2ba(self.__CTR,8)
            PRND = int2ba(PRND,8)
            NMAS = int2ba(DSM_NMAS,2)
            navDataADKD4 = navData(navData60Delayed,4)
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