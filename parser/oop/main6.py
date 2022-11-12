


from time import sleep
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.table import Table
import csv
from dataVisualisationSupport import updateLogs, Clock, DSM_Info, svTable


from dataAcquisition import readUbloxData
from dataTransformation_inputDataTransformation import ubloxWordsList2GalileoICD
from dataProcessingGalileoFrame_svKrootOsnmaMack import osnmaSplitter, mackParser
from dataProcessingGalileoFrame_svNavMessage import svConstellation
from dataProcessingOsnma_DSM import keyChain
from dataProcessingSupport import computeDelayedTime, weekSeconds2Time, DSM_Getter, concatenateBytes, checkRootKey
from logger import log_centralise
from bitarray import bitarray
from bitarray.util import int2ba, ba2int, ba2hex, hex2ba
from hashlib import sha256
from dataProcessingOsnma_Authenticator import NavDataAuthenticator


updatedTable = updateLogs()
Clock = Clock()
DSMInf = DSM_Info()
Satellites = svTable()

console = Console()
layout = Layout()

DSM_NMAS_Dict = {1:"Test",2:"Operational",3:"Don't Use"}
DSM_CDPKS_Dict = {1:"Nominal", 2:"End Of Chain", 3:"Chain Revoked", 4: "New Public Key", 5:"Publick Key Revoked"}

layout.split(
    Layout(name="header", size=1),
    Layout(ratio=1, name="main"),
    Layout(size=8, name="footer"),
)

layout["main"].split_row(Layout(name="body"), Layout(name="side", ratio=3))
layout["side"].update(
Align.left(
    Satellites
)
)




layout["header"].update(Clock)
layout["footer"].update(Align.center(updatedTable,vertical="top"))
layout["body"].update(Align.center(DSMInf,vertical="middle"))
layout["side"].update(Align.center(Satellites,vertical="middle"))


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

osnmaDivider = osnmaSplitter()
mackDivider = mackParser()
teslaKeyStatus = False
previous_key = False
currentDS = ""

# NavData Authentication Objects
authenticator = NavDataAuthenticator()

pemFileLocation = ".\parser\oop\OSNMA_PublicKey_20210920133026.pem"
timeSleep = 0.001
with Live(layout, screen=True, redirect_stderr=False) as live:
    try:
        while True:
            
            while ublox_words != None:
                sleep(timeSleep)
                pageProcessor.ublox2Galileo(ublox_words)
                svId = pageProcessor.getSvId()
                galCons.feedConstellation(svId, pageProcessor.getWordType(), pageProcessor.getData(), pageProcessor.getOsnma())
                svDataFrameStatus = galCons.getSvDataFrameCompleteStatus(svId)
                
                Satellites.updateParameters(galCons)
                
                if svDataFrameStatus and galCons.getSvOsnmaStatus(svId):
                    DSM_ID, DSM_BID, DSM_Block, DSM_NMAS, DSM_CID, DSM_CDPKS, NMAS_Header= DSM_Getter(galCons,svId)
                    DSM_Block = concatenateBytes(DSM_Block)
                    if DSM_NMAS <=2:
                        galCons.feedDSM(DSM_ID, DSM_BID, DSM_Block)
                        DSMInf.updateParameters( DSM_NMAS_Dict[DSM_NMAS], galCons.getCurrentDSMId(), galCons.getCurrentDSMBlocks(), galCons.getCurrentTotalDSMBlocks(),DSM_CID,DSM_CDPKS_Dict[DSM_CDPKS] , "unknown","unknown", "unknown","unkown","unkown")
                    if galCons.getCurrentDSMCompletenessStatus():
                            timeSleep = 0.1
                            if currentDS != galCons.getCurrentDS():
                                rootKeyStatus = checkRootKey(pemFileLocation, galCons.getCurrentM(NMAS_Header), galCons.getCurrentDS())
                                currentDS = galCons.getCurrentDS()
                            if rootKeyStatus:
                                hkroot = galCons.getCurrentKroot()
                                hkrootTime = galCons.getCurrentKrootTime()
                                hkrootTimeSeconds = galCons.getCurrentKrootTimeSeconds()
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
                                    keyStatus = chain.checkTeslaKeyAgainsRootKey(teslaKey, teslaKeyTime, teslaKeyTimeSeconds)
                                if previous_key == False:
                                    chain = keyChain(hkroot, hkrootTime, hkrootTimeSeconds, alpha, keyLength)
                                    keyStatus = chain.checkTeslaKeyAgainsRootKey(teslaKey, teslaKeyTime, teslaKeyTimeSeconds)
                                    previous_key = True
                                DSMInf.updateParameters( DSM_NMAS_Dict[DSM_NMAS], galCons.getCurrentDSMId(), galCons.getCurrentDSMBlocks(), galCons.getCurrentTotalDSMBlocks(),DSM_CID,DSM_CDPKS_Dict[DSM_CDPKS],teslaKey.hex(), hkroot.hex(),"WN:"+str(ba2int(hkrootTime[0:12]))+" TOW(h): "+str(ba2int(hkrootTime[12:])), rootKeyStatus, keyStatus)
                            svDataFrame = galCons.getSvDataFrame(svId)
                            svOsnmaFrame = galCons.getSvOsnmaFrame(svId)
                            timeBytes = galCons.getSvGST(svId)
                            # Self-Authentication
                            svOsnmaSelfStatus = authenticator.computeSelfAuthentication(timeBytes, svId, svDataFrame, svOsnmaFrame, keyLength, tagLength, DSM_NMAS)
                            galCons.setSvSelfAuthenticationStatus(svId, svOsnmaSelfStatus)
                            # Cross-Auhtencitacion
                            authenticator.computeCrossAuthentication(svId, timeBytes, svOsnmaFrame, keyLength, tagLength, DSM_NMAS, galCons)
                            crossAuthentication = authenticator.getCrossAuthenticationStatus()
                            galCons.setSvCrossAuthentication(svId, crossAuthentication)
                if svDataFrameStatus:
                    galCons.setSvDataFrameCompleteStatus(svId, False)
                    svDataFrameStatus = galCons.getSvDataFrameCompleteStatus(svId)
                    galCons.feedConstellation(svId, pageProcessor.getWordType(), pageProcessor.getData(), pageProcessor.getOsnma())
                ublox_words = pageReader.getUbloxWordsList()
    except KeyboardInterrupt:
        pass