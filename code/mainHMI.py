### Libraries
from time import sleep
from datetime import datetime

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.table import Table

from bitarray.util import ba2int

# Bespoke Libraries
from dataAcquisition import readUbloxData, readUbloxSerial
from dataTransformation import ubloxWordsList2GalileoICD
from dataProcessingOsnma_svKrootOsnmaMack import osnmaSplitter, mackParser
from dataProcessingGalileoFrame_Constellation import svConstellation
from dataProcessingOsnma_DSM import concatenateBytes, DSM_Getter
from dataProcessingOsnma_Authenticator import NavDataAuthenticator, keyChain, checkRootKey
from logger import log_centralise
## From the two following includings, comment the one you want to use
from dataVisualisationSupport_raspberry import updateLogs, Clock, DSM_Info, svTable 
#from dataVisualisationSupport import updateLogs, Clock, DSM_Info, svTable



##### Configuration Data

## Format of the log file and the csv input file (if program is configured as "Live", not to read test data)
now = datetime.now()
dt_string = now.strftime("%Y_%m_%d-%H_%M")
inputRecord = dt_string+".csv"
logFile = dt_string+".log"

## Configuration of Test/Live Data
# Location of the CSV for test data, with the list (Comma separated) of the ublox words, and timeSleep between page readings.
# Comment both lines for Real data
test_data = "./test_data/17_11_2022.csv"
timeSleep = 0.0001
#pageReader = readUbloxData(test_data, ',') # Uncomment if you want to use Test Data
pageReader = readUbloxSerial(inputRecord, '/dev/ttyACM0', 38400, True)

numGalSat = 36 # Number of Galileo Satellites

# Location of the GSC Public Key
pemFileLocation = "./code/OSNMA_PublicKey_20210920133026.pem"

## HMI Configuration
# Number of rows of shown logs
numRows = 4
sizeHeader = 1
ratioSVCommonInfo = 3
sizeFooter = 8
ratioMain = 2
# Log configuration 
log_centralise(
            "a", # "a" for append 
            logFile, # Name of file 
            '%(asctime)s,%(levelname)s,%(message)s') # Format of logging
#####

updatedTable = updateLogs(logFile,numRows)
Clock = Clock()
DSMInf = DSM_Info()
Satellites = svTable()

console = Console()
layout = Layout()

DSM_NMAS_Dict = {1:"Test",2:"Operational",3:"Don't Use"}
DSM_CDPKS_Dict = {1:"Nominal", 2:"End Of Chain", 3:"Chain Revoked", 4: "New Public Key", 5:"Publick Key Revoked"}

layout.split(
    Layout(name="header", size=sizeHeader),
    Layout(ratio=ratioMain, name="main"),
    Layout(size=sizeFooter, name="footer"),
)

layout["main"].split_row(Layout(name="body"), Layout(name="side", ratio=ratioSVCommonInfo))
layout["side"].update(
Align.left(
    Satellites
)
)


layout["header"].update(Clock)
layout["footer"].update(Align.center(updatedTable,vertical="top"))
layout["body"].update(Align.center(DSMInf,vertical="middle"))
layout["side"].update(Align.center(Satellites,vertical="middle"))





## Set-Up of objects
# Data Adquisition (Ublox Words Reader)
ublox_words = pageReader.getUbloxWordsList()

# Data Transformation (From Ublow Words to Galileo ICD)
pageProcessor = ubloxWordsList2GalileoICD()

# Constellation Object Initialisation
galCons = svConstellation(numGalSat) #currently there are up to 36 Galileo Satellites

osnmaDivider = osnmaSplitter()
mackDivider = mackParser()
teslaKeyStatus = False
previous_key = False
currentDS = ""

# NavData Authentication Objects
authenticator = NavDataAuthenticator()


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
                            #timeSleep = 0.00001
                            if currentDS != galCons.getCurrentDS():
                                rootKeyStatus = checkRootKey.checkRootKeyValidity(pemFileLocation, galCons.getCurrentM(NMAS_Header), galCons.getCurrentDS())
                                currentDS = galCons.getCurrentDS()
                            if rootKeyStatus== True or rootKeyStatus == False:
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
                            svOsnmaSelfStatus = authenticator.getSelfAuthentication(timeBytes, svId, svDataFrame, svOsnmaFrame, keyLength, tagLength, DSM_NMAS)
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