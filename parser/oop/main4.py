# This program tests the Self - Authentication featuere for a set of satellites and test data

from dataAcquisition import readUbloxData
from dataTransformation_inputDataTransformation import ubloxWordsList2GalileoICD
from dataProcessingGalileoFrame_svKrootOsnmaMack import osnmaSplitter, mackParser
from dataProcessingGalileoFrame_svNavMessage import svConstellation
from dataProcessingSupport import computeDelayedTime, navData, weekSeconds2Time
from time import sleep
import logging

import csv
import hmac
from bitarray import bitarray
from bitarray.util import int2ba, ba2int, hex2ba, ba2hex

keyLength = 128
tagLength = 40

# Data Adquisition (Ublox Words Reader)
pageReader = readUbloxData('./test_data/25-01-2022.csv', ',')
ublox_words = pageReader.getUbloxWordsList()

# Data Transformation (From Ublow Words to Galileo ICD)
pageProcessor = ubloxWordsList2GalileoICD()

# Constellation Object Initialisation
galCons = svConstellation(36) #currently there are up to 36 Galileo Satellites

# OSNMA functions
osnmaDivider = osnmaSplitter()
authenticator = mackParser()



while ublox_words != None:
    
    # Getting data from the Ublox Words, converting it to Galileo ICD and feed constellation
    # Only SV number, WordType, Data and OSNMA (Reserved1) is needed.
    pageProcessor.ublox2Galileo(ublox_words)
    svId = pageProcessor.getSvId()
    wordType = pageProcessor.getWordType()
    data = pageProcessor.getData()
    osnma = pageProcessor.getOsnma()
    galCons.feedConstellation(svId, wordType, data, osnma)
    # Each time we feed the Constellation, check if any satellite has a completed SubFrame (to be improved in the future)
    
    if galCons.getSvDataFrameCompleteStatus(svId): # Check if we have a completed subframe and the satellite emits OSNMA
        if galCons.getSvOsnmaDistributionStatus(svId):
            
            timeDataFrameBytes = galCons.getSvGST(svId)
            timeT0Bytes = computeDelayedTime(timeDataFrameBytes,30)
            timeT0BitArray = bitarray()
            timeT0BitArray.frombytes(timeT0Bytes)
            timeNavDataBytes = computeDelayedTime(timeDataFrameBytes,60)
            try:
                
                osnmaTag0 = galCons.getSvOsnmaOnGST(svId, timeT0Bytes)
                osnmaDivider.osnmaSubFrame2hkRootMack(osnmaTag0)
                
                if osnmaDivider.getNMAS() == 1 or osnmaDivider.getNMAS() == 2:
                    NMAS = int2ba(osnmaDivider.getNMAS(),2)
                    
                    # Case Self-Authentication
                    PRNA = int2ba(svId,8)
                    CTR = int2ba(1,8)
                    
                    authenticator.parseMackMessage(osnmaDivider.getMack(), keyLength, tagLength)
                    
                    tag0 = authenticator.getTag0()
                    DSM_ID = osnmaDivider.getDSMId()
                    DSM_BID = osnmaDivider.getDSMBlockId()
                    index = 2
                    
                    #print("DSM ID:",DSM_ID, "DSM Block ID:", DSM_BID)
                    
                    osnmaKey = galCons.getSvOsnmaOnGST(svId, timeDataFrameBytes)
                    osnmaDivider.osnmaSubFrame2hkRootMack(osnmaKey)
                    authenticator.parseMackMessage(osnmaDivider.getMack(), keyLength, tagLength)
                    key = authenticator.getTeslaKey()
                    
                    ADKD0_NavData = galCons.getSvDataOnGST(svId, timeNavDataBytes)
                    
                    
                    
                    ADKD0_NavData = navData(ADKD0_NavData)
                    m = PRNA+timeT0BitArray+CTR+NMAS+ADKD0_NavData
                    m.fill()
                    h = bitarray()
                    h.frombytes(hmac.digest(key, m.tobytes(), 'sha256'))
                    h = h[:40]
                    #print("Tag0 Time:",weekSeconds2Time(ba2int(timeT0BitArray[12:])))
                    
                    
                    print(svId, timeDataFrameBytes)
                    if tag0 == h.tobytes():
                        pass
                        #print("ADKD0 NavData:",ADKD0_NavData.tobytes())
                        print("Sat:",svId, "Self-Authenticated", "Computed hash:", tag0, "Expected Hash:", h.tobytes())
                    else: 
                        pass
                        print("Sat:",svId, "NOT Self-Authenticated!!", "Computed hash:", tag0, "Expected Hash:", h.tobytes())
                    #print("OSNMA Status:",galCons.getSvOsnmaDistributionStatus(svId))
                    galCons.setSvOsnmaDistributionStatus(svId)
                    #print("OSNMA Status:",galCons.getSvOsnmaStatus(svId),"\n")
            except: pass
        else: 
            timeDataFrameBytes = galCons.getSvGST(svId)
            timeDataFrame = bitarray()
            timeDataFrame.frombytes(timeDataFrameBytes)
            
            #print(weekSeconds2Time(ba2int(timeDataFrame[12:])),": Satellite: ",svId, " is not transmitting OSNMA","\n")
        galCons.feedConstellation(svId, wordType, data, osnma)
    ublox_words = pageReader.getUbloxWordsList()