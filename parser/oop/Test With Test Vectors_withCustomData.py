# Test With Test Vectors provided in "OSNMA Receiver Guidelines for the Test Phase, issue 1.0, November 2021"

import csv
import dataProcessingGalileoFrame_inputDataTransformation
from bitarray import bitarray
from bitarray.util import int2ba, ba2int, hex2ba, ba2hex
from dataProcessingGalileoFrame_svNavMessage import svNavMessage
from dataProcessingGalileoFrame_svNavMessage import svKrootOsnmaMack
from dataProcessingGalileoFrame_svNavMessage import NavMessageAuthenticator
import hmac

sat = svNavMessage()
pageProcessor  = dataProcessingGalileoFrame_inputDataTransformation.testVectors2GalileoICD()
osnmaDivider = svKrootOsnmaMack()


satID = 14 #Example in Test Vectors
CTR_self = 1 #For Self-Authentication   
key = int2ba(0x4235FF797019E2EFD3CB72780E861FED,128)
tag0 = int2ba(0xE094B3FBA5,40)
tag0_2 = int2ba(0x25CAEECF3E,40)
keysize = 128
tagSize = 40

###### Process MACK

MACK1 =  [b'n\xb8]P', b'\xc4i\x83\x8a', b'\xa81\xb0W', b'\x0b\x00\xd4\x8e', b'\xa0\r\xc6!', b'\x03@\xf0\xc9', b'\xa1\x9a\x0e\xc3', b'V\x1c\x18Y', b'P\x1f\x00\x8e', b'J\x9e\xee\x99', b'$\xc2\x16\xb4', b'bD\x90\x11', b'\xab\x956*', b'b\xd1\x84\x98', b'\xa5\xa9\x00\x00']
MACK2 = [b'\x9btC\x89', b'\xddb\xf3\xa2', b'\xf0\x18\x0e\xb9', b'\x07\x00\xb1~', b'aWh\xff', b'@I\xb9\xe4', b'm\xc6\r\x01', b'\xd6|\x1a\xec', b'R\x0e\xc3@', b'\xe2\xc5=\xd0', b'\x0b\x00\x0f^', b'I\xdd\x9bu', b'g\x1a?7', b'\xbe:G{', b'\x83b\x00\x00']


MACK1_list = MACK1
MACK2_list = MACK2


authenticator1 = NavMessageAuthenticator()
authenticator2 = NavMessageAuthenticator()

authenticator1.parseMackMessage(MACK1_list, keysize, tagSize)
authenticator2.parseMackMessage(MACK2_list, keysize, tagSize)

tag01 = bitarray()
tag01.frombytes(authenticator1.getTag0())
tag02 = bitarray()
tag02.frombytes(authenticator2.getTag0())

key1 = bitarray()
key2 = bitarray() 
key1.frombytes(authenticator1.getTeslaKey())
key2.frombytes(authenticator2.getTeslaKey())


key = key2

print("########################################")
print("Tag0_1: ",ba2hex(tag01))
print("Tag0_2: ",ba2hex(tag02))




print("Key1:",ba2hex(key1))
print("Key2:",ba2hex(key2))

print("########################################")
###### Process NavPage

with open('.\parser\oop\iNav_TestVectors_customData.csv') as csvfile:
    reader = csv.reader(csvfile)
    lista = list(reader)


def adkd0computeOsnmaTime (GST_T0):
    b = bitarray()
    b.frombytes(GST_T0)
    b_WN = ba2int(b[0:12])
    b_TOW = b[-20:]
    b_TOW = ba2int(b_TOW)+30
    if b_TOW == 604800:
        b_TOW = 0
        b_WN = b_WN + 1
    osnmaTime = int2ba(b_WN,12)+int2ba(b_TOW,20)
    return osnmaTime.tobytes()

def navData(subFrame):
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

for row in lista:
    evenPage = int(row[0],16)
    oddPage = int(row[1],16)
    pageProcessor.testVec2Galileo(evenPage, oddPage)
    sat.subFrameSequence(pageProcessor.getWordType(),pageProcessor.getData(),pageProcessor.getOsnma())
    if sat.getDataFrameCompleteStatus():
        timeDataFrame = sat.getT0()
        timeBitArray = bitarray()
        timeBitArray.frombytes(timeDataFrame)
        print("WN DataFrame", ba2int(timeBitArray[0:12]),"; TOW DataFrame", ba2int(timeBitArray[12:]))
        timeOsnmaBitArray = bitarray()
        adkd0computeOsnmaTime(sat.getT0())
        timeOsnmaBitArray.frombytes(adkd0computeOsnmaTime(sat.getT0()))
        print("WN OSNMA", ba2int(timeOsnmaBitArray[0:12]),"; TOW OSNMA", ba2int(timeOsnmaBitArray[12:]))
        #print("Hex OSNMA: ",ba2hex(timeOsnmaBitArray))
        ADKD0_NavData_filled = navData(sat.getDataSubframe())
        PRNA = int2ba(satID,8)
        CTR = int2ba(CTR_self,8)
        NMAS = bitarray('01')
        print("PRNA",ba2hex(PRNA))
        print("GST_OSNMA",ba2hex(timeOsnmaBitArray))
        print("CTR",ba2hex(CTR))
        print("NMAS",NMAS)
        #print("NavData",ba2hex(ADKD0_NavData_filled))
        m = PRNA+timeOsnmaBitArray+CTR+NMAS+ADKD0_NavData_filled
        m.fill()
        print("m0:",ba2hex(m))
        ADKD0_NavData_filled.fill()
        print("ADKD nav Data",ba2hex(ADKD0_NavData_filled))
        print("Key:",ba2hex(key))
        h = bitarray()
        h.frombytes(hmac.digest(key.tobytes(), m.tobytes(), 'sha256'))
        h = h[:40]
        
        print("Computed Hash: ", ba2hex(h), "Expected Hash: ", ba2hex(tag01))
        if ba2hex(h) == ba2hex(tag01):
            print("Self-Authentication is proven")
        else: print("Cannot Prove Self-Authetication")
print("########################################")