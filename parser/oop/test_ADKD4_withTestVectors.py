# Test With Test Vectors provided in "OSNMA Receiver Guidelines for the Test Phase, issue 1.0, November 2021"

import csv
from dataTransformation_inputDataTransformation import testVectors2GalileoICD
from bitarray import bitarray
from bitarray.util import int2ba, ba2int, hex2ba, ba2hex
from dataProcessingGalileoFrame_svNavMessage import svNavMessage
from dataProcessingGalileoFrame_svNavMessage import svKrootOsnmaMack
from dataProcessingGalileoFrame_svKrootOsnmaMack import osnmaSplitter, mackParser
from dataProcessingSupport import computeDelayedTime, weekSeconds2Time, DSM_Getter, concatenateBytes,checkRootKey, navData
import hmac
mackDivider1 = mackParser()
mackDivider2 = mackParser()
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



svId = 1 #Example in Test Vectors
sat = svNavMessage(svId)
osnmaDivider = svKrootOsnmaMack()

keysize = 128
tagSize = 40
CTR_self = 1 #For Self-Authentication   
key = int2ba(0x4235FF797019E2EFD3CB72780E861FED,128)
pageProcessor = testVectors2GalileoICD()

mackDivider1.parseMackMessage(MACK1_list, keysize, tagSize)
mackDivider2.parseMackMessage(MACK2_list, keysize, tagSize)


with open('.\parser\oop\iNav_TestVectors.csv') as csvfile:
    reader = csv.reader(csvfile)
    lista = list(reader)
    



for row in lista:
    evenPage = int(row[0],16)
    oddPage = int(row[1],16)
    pageProcessor.testVec2Galileo(evenPage, oddPage)
    sat.subFrameSequence(pageProcessor.getWordType(),pageProcessor.getData(),pageProcessor.getOsnma())


tags1 = mackDivider1.getTagsAndInfo()
tags2 = mackDivider2.getTagsAndInfo()



CTR = 2
for item in tags2:
    b = bitarray()
    b.frombytes(item['Tag'])
    #print(CTR,ba2hex(b), item['PRND'], item['ADKD'])
    if  item['PRND'] == 255:
        #print(item['PRND'])
        CTRi =CTR
    CTR+=1
    
CTR = 2
for item in tags1:
    b = bitarray()
    b.frombytes(item['Tag'])
    print(CTR,ba2hex(b), item['PRND'], item['Tag'].hex())
    if  item['PRND'] == 255:
        #print(item['PRND'])
        CTRi = CTR
        print(item['Tag'])
    CTR+=1
    
navDataADKD4 = sat.getDataSubframe()
navDataADKD4 = navData(navDataADKD4,4)
#print(len(navDataADKD4))
#print(ba2hex(navDataADKD4))
#print('00000001FFFFFF12907889E25274CE00D7FF801C8')

NMAS = bitarray('01')
CTR = int2ba(CTRi,8)
PRND = int2ba(svId,8)

navDataTime = sat.getT0()

osnmaTime = computeDelayedTime(navDataTime,-30)
b = bitarray()
b.frombytes(osnmaTime)
print("WN DataFrame", ba2int(b[0:12]),"; TOW DataFrame", ba2int(b[12:]))

m = PRND+PRND+b+CTR+NMAS+navDataADKD4
m.fill()
print("m: ",ba2hex(m))

h = bitarray()
h.frombytes(hmac.digest(mackDivider2.getTeslaKey(), m, 'sha256'))
h= h[:tagSize]
print(h.tobytes())


