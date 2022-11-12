from bitarray import bitarray
from bitarray.util import int2ba, ba2int, hex2ba, ba2hex
import csv
import hmac

from dataAcquisition import readUbloxData
from dataProcessingSupport import weekSeconds2Time, navData
from dataProcessingGalileoFrame_inputDataTransformation import ubloxWordsList2GalileoICD
from dataProcessingGalileoFrame_svNavMessage import svConstellation
from dataProcessingGalileoFrame_svNavMessage import svNavMessage
from dataProcessingGalileoFrame_svNavMessage import svKrootOsnmaMack
from dataProcessingGalileoFrame_svNavMessage import NavMessageAuthenticator

keysize = 128
tagSize = 40

osnmaDivider = svKrootOsnmaMack()
pageReader = readUbloxData('./test_data/25-01-2022.csv', ',')
pageProcessor = ubloxWordsList2GalileoICD()
authenticator = NavMessageAuthenticator()
galCons = svConstellation(36) #currently there are up to 36 Galileo Satellites

with open('./test_data/25-01-2022.csv') as csvfile:
    reader = csv.reader(csvfile)
    lista = list(reader)

sat = svNavMessage()
ublox_words = pageReader.getUbloxWordsList()

CTR_self = 1


def computeDelayedTime (GST_T0,delay):
    b = bitarray()
    b.frombytes(GST_T0)
    b_WN = ba2int(b[0:12])
    b_TOW = b[-20:]
    b_TOW = ba2int(b_TOW)-delay
    if b_TOW == 604800:
        b_TOW = 0
        b_WN = b_WN -1
    osnmaTime = int2ba(b_WN,12)+int2ba(b_TOW,20)
    return osnmaTime.tobytes()


while ublox_words != None:
    pageProcessor.ublox2Galileo(ublox_words)
    print(pageProcessor.getSvId())
    galCons.feedConstellation(pageProcessor.getSvId(), pageProcessor.getWordType(), pageProcessor.getData(), pageProcessor.getOsnma())
    if len(galCons.notifier()) != 0:
        #print(galCons.notifier())
        for sv in galCons.notifier():
            if galCons.getSvOsnmaDistributionStatus(sv):
                # Case Self-Authentication
                try:
                    if sv == 11:
                        timeDataFrame = galCons.getSvGST(sv)
                        timeBitArray = bitarray()
                        timeBitArray.frombytes(timeDataFrame)
                        timeBitArray[12:]
                        time0Bytes = computeDelayedTime(timeDataFrame,30)
                        timet0 = bitarray()
                        timet0.frombytes(time0Bytes)
                        
                        timeNavDataBytes = computeDelayedTime(timeDataFrame,60)
                        timeNavData = bitarray()
                        timeNavData.frombytes(timeNavDataBytes)
                        print()
                        print("Sat Num:", sv)
                        print("WN Current", ba2int(timeBitArray[0:12]),"; TOW Current", ba2int(timeBitArray[12:]), "Time Hex", ba2hex(timeBitArray))
                        
                        PRNA = int2ba(sv,8)
                        CTR = int2ba(1,8)
                        NMAS = bitarray('01')
                        
                        osnmaTag0 = galCons.getSvOsnmaOnGST(sv, time0Bytes)
                        osnmaDivider.osnmaSubFrame2hkRootMack(osnmaTag0)
                        authenticator.parseMackMessage(osnmaDivider.getMack(),128,40)
                        tag0 = bitarray()
                        tag0.frombytes(authenticator.getTag0())
                        print("Parsed Mack",authenticator.getParsedMackMessage())
                        
                        osnmaKey = galCons.getSvOsnmaOnGST(sv, timeDataFrame)
                        osnmaDivider.osnmaSubFrame2hkRootMack(osnmaKey)
                        authenticator.parseMackMessage(osnmaDivider.getMack(),128,40)
                        key = bitarray()
                        key.frombytes(authenticator.getTeslaKey())
                        print("Key =", ba2hex(key))
                        
                        ADKD0_NavData = galCons.getSvDataOnGST(11, timeNavDataBytes)
                        ADKD0_NavData = navData(ADKD0_NavData)
                        m = PRNA+timet0+CTR+NMAS+ADKD0_NavData
                        m.fill()
                        print("m0:", ba2hex(m))
                        h = bitarray()
                        h.frombytes(hmac.digest(key.tobytes(), m.tobytes(), 'sha256'))
                        h = h[:40]
                        print("Tag0 (Expected Hash) :", ba2hex(tag0))
                        print("Computed Hash: ", ba2hex(h))
                        if ba2hex(h) == ba2hex(tag0):
                            print("Self-Authentication is proven")
                        
                        galCons.feedConstellation(pageProcessor.getSvId(), pageProcessor.getWordType(), pageProcessor.getData(), pageProcessor.getOsnma()) #WorkAround to avoid repeated CompleteStatus
                        
                except: print("Not Enough Data to Compute Self-Authentication")
                
                # Case Cross - Authentication
    ublox_words = pageReader.getUbloxWordsList()
