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


satID = 1 #Example in Test Vectors
CTR_self = 1 #For Self-Authentication   
key = int2ba(0x4235FF797019E2EFD3CB72780E861FED,128)
tag0 = int2ba(0xE094B3FBA5,40)
tag0_2 = int2ba(0x25CAEECF3E,40)
keysize = 128
tagSize = 40

###### Process MACK

MACK1 = int2ba(0xE094B3FBA533A6A6B55DFED505055EBEC4E3A8FF40B580AEB151190578A85B879301C6B3E3315F471B0517B98FD42A4AFD0EA36D1DA2DE406B930000,480) #Received at WN = 1145; TOW = 0 
MACK2 = int2ba(0x25CAEECF3EEDC68A2BA7BD7A1B05354C3819942405FF5C3DDA4801C61D0C9AB88E1A0674FEF6A5B221C14235FF797019E2EFD3CB72780E861FED0000,480)  #Received at WN = 1145; TOW = 30

MACK1_list = [None for i in range(15)]
MACK2_list = [None for i in range(15)]

a = 0 
b = 32
i = 0
for mack in MACK1_list:
    MACK1_list[i] = MACK1[a:b].tobytes()
    a = b
    b = b+32
    i+=1

a = 0 
b = 32
i = 0

for mack in MACK2_list:
    MACK2_list[i] = MACK2[a:b].tobytes()
    a = b
    b = b+32
    i+=1

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


print("########################################")
print("Tag0_1, Received at WN = 1145; TOW = 0 : ",ba2hex(tag01))
print("Tag0_2, Received at WN = 1145; TOW = 30: ",ba2hex(tag02))




print("Key1, Received at WN = 1145 TOW = 0 :",ba2hex(key1))
print("Key2, Received at WN = 1145 TOW = 30 :",ba2hex(key2))

if ba2int(tag01) == ba2int(tag0):
    print("Tag 0_1 is properly calculated")
if ba2int(tag02) == ba2int(tag0_2):
    print("Tag 0_2 is properly calculated")

if ba2int(key2) == ba2int(key):
    print("Key2 is properly calculated")

print("########################################")
###### Process NavPage

with open('.\parser\oop\iNav_TestVectors.csv') as csvfile:
    reader = csv.reader(csvfile)
    lista = list(reader)


def adkd0computeOsnmaTime (GST_T0 = bytearray()):
    b = bitarray()
    b.frombytes(GST_T0)
    b_WN = b[0:12]
    b_TOW = b[-20:]
    b_TOW = ba2int(b_TOW)+30
    if b_TOW == 604800:
        b_TOW = 0
        b_WN = ba2int(b_WN) + 1
    osnmaTime = int2ba(b_WN,12)+int2ba(b_TOW,20)
    return osnmaTime.tobytes()

def navData(subFrame = bytearray()):
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
        timeOsnmaBitArray.frombytes(adkd0computeOsnmaTime(sat.getT0()))
        print("WN OSNMA", ba2int(timeOsnmaBitArray[0:12]),"; TOW OSNMA", ba2int(timeOsnmaBitArray[12:]))
        #print("Hex OSNMA: ",ba2hex(timeOsnmaBitArray))
        ADKD0_NavData_filled = navData(sat.getDataSubframe())
        PRNA = int2ba(satID,8)
        CTR = int2ba(CTR_self,8)
        NMAS = bitarray('01')
        print("PRNA",ba2hex(PRNA))
        print("GST_OSNMA",ba2hex(timeOsnmaBitArray))
        print("CTR",ba2hex(PRNA))
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
        
        print("Computed Hash: ", ba2hex(h), "Expected Hash: ", ba2hex(tag0))
        if ba2hex(h) == ba2hex(tag0):
            print("Self-Authentication is proven")
        else: print("Cannot Prove Self-Authetication")
print("########################################")