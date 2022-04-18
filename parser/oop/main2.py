import dataAcquisition
import dataProcessingGalileoFrame_inputDataTransformation
import dataProcessingGalileoFrame_svNavMessage
from dataProcessingGalileoFrame_svNavMessage import svConstellation as galConstellation
from dataProcessingGalileoFrame_svNavMessage import svNavMessage
from dataProcessingGalileoFrame_svNavMessage import svKrootOsnmaMack
from dataProcessingGalileoFrame_svNavMessage import NavMessageAuthenticator
from bitarray import bitarray
from bitarray.util import int2ba, ba2int, hex2ba, ba2hex
import csv
import hmac
import hashlib

keysize = 128
tagSize = 40


osnmaDivider = svKrootOsnmaMack()
pageReader = dataAcquisition.readUbloxData('./test_data/25-01-2022.csv', ',')
pageProcessor = dataProcessingGalileoFrame_inputDataTransformation.ubloxWordsList2GalileoICD()

galCons = galConstellation(36) #currently there are up to 36 Galileo Satellites

with open('./test_data/25-01-2022.csv') as csvfile:
    reader = csv.reader(csvfile)
    lista = list(reader)


def weekSeconds2Time(weekSeconds): #function to return a string of hours in HH:mm:ss (to be updated)
        hours = weekSeconds/3600
        while hours >= 24:
            hours = hours - 24
        hour = int(hours)
        minutes = hours-hour #minutes in hour format
        minute = minutes*60  #minuts in minut format
        seconds = minute - int (minute) # seconds in minut format
        second = int(seconds*60) #seconds in second format
        time = str(hour).zfill(2) + ":" + str(int(minute)).zfill(2) + ":" + str(second).zfill(2)
        return  time

authenticator = NavMessageAuthenticator()
sat = svNavMessage()
ublox_words = []
ublox_words = pageReader.getUbloxWordsList()

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



def navData(subFrame):
    word = bitarray()
    b = bitarray()
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

satID = 11
CTR_self = 1

while ublox_words != None:
    pageProcessor.ublox2Galileo(ublox_words)
    if pageProcessor.getSvId() == satID:
        sat.subFrameSequence(pageProcessor.getWordType(),pageProcessor.getData(),pageProcessor.getOsnma())
        
        if sat.getDataFrameCompleteStatus() & sat.getOsnmaDistributionStatus():
            timeDataFrame = sat.getT0()
            timeBitArray = bitarray()
            timeBitArray.frombytes(timeDataFrame)
            
            timet0 = bitarray()
            timet0Bytes = computeDelayedTime(sat.getT0(),30)
            timet0.frombytes(timet0Bytes)
            
            timeNavData = bitarray()
            timeNavDataBytes = computeDelayedTime(sat.getT0(),60)
            timeNavData.frombytes(timeNavDataBytes)
            print("Satellite:", satID)
            print("WN Key/Current", ba2int(timeBitArray[0:12]),"; TOW Key/Current", ba2int(timeBitArray[12:]))
            print("WN Tag0", ba2int(timet0[0:12]),"; TOW tag0", ba2int(timet0[12:]))
            print("WN NavData", ba2int(timeNavData[0:12]),"; TOW NavData", ba2int(timeNavData[12:]))
            
            PRNA = int2ba(satID,8)
            CTR = int2ba(CTR_self,8)
            NMAS = bitarray('01')
            #print("PRNA",ba2hex(PRNA))
            #print("CTR",ba2hex(CTR))
            #print("NMAS",NMAS)
            
            #print("Data Delayed 60 sec",sat.getDataOnGST(timeNavDataBytes))
            #print("Current Data",sat.getDataSubframe())
            

            
            try:
                osnmaDivider.osnmaSubFrame2hkRootMack(sat.getOsnmaOnGST(timet0Bytes))
                authenticator.parseMackMessage(osnmaDivider.getMack(), keysize, tagSize)
                #print("Mack Delayed 30 sec:",osnmaDivider.getMack())
                
                tag0 = bitarray()
                tag0.frombytes(authenticator.getTag0())
                print("Tag0 is:",ba2hex(tag0))
                osnmaDivider.osnmaSubFrame2hkRootMack(sat.getOsnmaOnGST(sat.getT0()))
                authenticator.parseMackMessage(osnmaDivider.getMack(), keysize, tagSize)
                #print("Current Mack is:",osnmaDivider.getMack())
                key = bitarray()
                key.frombytes(authenticator.getTeslaKey())
                print("Key is: ",ba2hex(key) )
                ADKD0_NavData_filled = navData(sat.getDataOnGST(timeNavDataBytes))
                
                m = PRNA+timet0+CTR+NMAS+ADKD0_NavData_filled
                m.fill()
                print("m0:",ba2hex(m))
                h = bitarray()
                h.frombytes(hmac.digest(key.tobytes(), m.tobytes(), 'sha256'))
                h = h[:40]
                print("Computed Hash: ", ba2hex(h), "Expected Hash: ", ba2hex(tag0))
                ADKD0_NavData_filled.fill()
                print("Delayed ADKD nav Data",ba2hex(ADKD0_NavData_filled))
                if ba2hex(h) == ba2hex(tag0):
                    print("Self-Authentication is proven")
                else: print("Cannot Prove Self-Authetication")
            except: print("Not enough previous data available to compute Self-Authentication")
            print()
    ublox_words = pageReader.getUbloxWordsList()
