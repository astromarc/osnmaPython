## This Program Test the OSNMA Self-Authentication from a CSV Test Data


from dataAcquisition import readUbloxData
from dataTransformation_inputDataTransformation import ubloxWordsList2GalileoICD
from dataProcessingGalileoFrame_svKrootOsnmaMack import osnmaSplitter, mackParser
from dataProcessingGalileoFrame_svNavMessage import svConstellation
from dataProcessingOsnma_DSM import keyChain
from dataProcessingSupport import computeDelayedTime, weekSeconds2Time, DSM_Getter, concatenateBytes,checkRootKey, navData
from logger import log_centralise
from bitarray import bitarray
from bitarray.util import int2ba, ba2int, ba2hex, hex2ba
from hashlib import sha256
import hmac
from dataProcessingOsnma_Authenticator import NavDataAuthenticator
from time import sleep


log_centralise(
            "a", 
            "Test.log", 
            '%(asctime)s.%(msecs)d,%(levelname)s,%(message)s')

## Set-Up of objects

# Data Adquisition (Ublox Words Reader)
pageReader = readUbloxData('./test_data/25-01-2022.csv', ',')
ublox_words = pageReader.getUbloxWordsList()

# Data Transformation (From Ublow Words to Galileo ICD)
pageProcessor = ubloxWordsList2GalileoICD()

# Constellation Object Initialisation
galCons = svConstellation(36) #currently there are up to 36 Galileo Satellites

# OSNMA functions
osnmaDivider = osnmaSplitter()
mackDivider = mackParser()


filename2 = ".\parser\oop\OSNMA_PublicKey_20210920133026.pem"

previous_key = False
currentDS = ""
previous_tag0 = None
teslaKeyStatus = False


while ublox_words != None:
    # Process Page
    pageProcessor.ublox2Galileo(ublox_words)
    # Feeding Galileo Constellation
    svId = pageProcessor.getSvId()
    galCons.feedConstellation(svId, pageProcessor.getWordType(), pageProcessor.getData(), pageProcessor.getOsnma())
    svDataFrameStatus = galCons.getSvDataFrameCompleteStatus(svId)

    if svDataFrameStatus and galCons.getSvOsnmaStatus(svId):

        DSM_ID, DSM_BID, DSM_Block, DSM_NMAS, DSM_CID, DSM_CIDStatus, NMAS_Header = DSM_Getter(galCons,svId)
        DSM_Block = concatenateBytes(DSM_Block)
        if DSM_NMAS <=2:
            galCons.feedDSM(DSM_ID, DSM_BID, DSM_Block)
        if galCons.getCurrentDSMCompletenessStatus():
            
            # Root Tesla Key verification
            if currentDS != galCons.getCurrentDS():
                rootKeyStatus = checkRootKey(filename2, galCons.getCurrentM(NMAS_Header), galCons.getCurrentDS())
                currentDS = galCons.getCurrentDS()
            if rootKeyStatus:
                hkroot = galCons.getCurrentKroot()
                hkrootTime = galCons.getCurrentKrootTime()
                hkrootTimeSeconds = galCons.getCurrentKrootTimeSeconds()
                
                # Tesla Key Authenticator
                teslaKeyTime = galCons.getSvGST(svId)
                teslaKeyTimeSeconds = galCons.getSvT0Seconds(svId)
                osnmaTeslaKey = galCons.getSvOsnmaOnGST(svId, teslaKeyTime)
                osnmaDivider.osnmaSubFrame2hkRootMack(osnmaTeslaKey)
                keyLength = galCons.getCurrentKeySize()
                tagLength = galCons.getCurrentTagSize()
                mackDivider.parseMackMessage(osnmaDivider.getMack(), keyLength, tagLength)
                teslaKey = mackDivider.getTeslaKey()
                alpha = galCons.getCurrentAlpha()
                
                if previous_key == True:
                    teslaKeyStatus = chain.checkTeslaKeyAgainsRootKey(teslaKey, teslaKeyTime, teslaKeyTimeSeconds)
                if previous_key == False: #we will need to check key validity
                    chain = keyChain(hkroot, hkrootTime, hkrootTimeSeconds, alpha, keyLength)
                    teslaKeyStatus = chain.checkTeslaKeyAgainsRootKey(teslaKey, teslaKeyTime, teslaKeyTimeSeconds)
                    previous_key = True
            ## Self-Authentication
            if teslaKeyStatus:
                svDataFrame = galCons.getSvDataFrame(svId)
                svOsnmaFrame = galCons.getSvOsnmaFrame(svId)
                timeBytes = galCons.getSvGST(svId)
                authenticator = NavDataAuthenticator()
                svOsnmaSelfStatus = authenticator.computeSelfAuthentication(timeBytes, svId, svDataFrame, svOsnmaFrame, keyLength, tagLength, DSM_NMAS)
                galCons.setSvSelfAuthenticationStatus(svId, svOsnmaSelfStatus)
                #print(svOsnmaSelfStatus)
            ## Cross-Authentication
                authenticator.computeCrossAuthentication(svId, timeBytes, svOsnmaFrame, keyLength, tagLength, DSM_NMAS, galCons)
                crossAuthentication = authenticator.getCrossAuthenticationStatus()
                galCons.setSvCrossAuthentication(svId, crossAuthentication)
                print(svId)
                #print(svOsnmaSelfStatus)
                print(crossAuthentication)
                if svId == 14:
                    print(galCons.getSvCrossAuthenticationStatus(11))
                print('\n')
                
    if svDataFrameStatus:
        galCons.setSvDataFrameCompleteStatus(svId, False)
        svDataFrameStatus = galCons.getSvDataFrameCompleteStatus(svId)
        galCons.feedConstellation(svId, pageProcessor.getWordType(), pageProcessor.getData(), pageProcessor.getOsnma())

    ublox_words = pageReader.getUbloxWordsList()