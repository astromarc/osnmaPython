# word_types_sequence = [(2,), (4,), (6,), (7,9), (8,10), (0,), (0,), (0,), (0,), (0,), (1,), (3,), (5,), (0,), (0,)]

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
    
def computeDelayedTime (GST_T0,delay):
    #it assumes that a delay positive means you want to get an "earlier" time
    #e.g., time 14:30 and delay 30 will return 14:00, whilst delay -30 will return 15:00
    from bitarray import bitarray
    from bitarray.util import int2ba, ba2int
    b = bitarray()
    b.frombytes(GST_T0)
    b_WN = b[0:12]
    b_TOW = b[12:]
    if delay >=0:
        i_WN = ba2int(b_WN)
        i_TOW = ba2int(b_TOW) - delay
        if i_TOW < 0:
            i_WN = i_WN - 1
            i_TOW = 7*24*3600 - i_TOW

    if delay <0:
        i_WN = ba2int(b_WN)
        i_TOW = ba2int(b_TOW) - delay
        if i_TOW> 604799:
            i_WN = i_WN + 1
            i_TOW = 604799 - (604799+delay+30)

    b_WN = int2ba(i_WN,12)
    b_TOW = int2ba(i_TOW,20)
    osnmaTime = b_WN+b_TOW
    return osnmaTime.tobytes()


def DSM_Getter(galCons, svId):
    from dataProcessingGalileoFrame_svKrootOsnmaMack import osnmaSplitter
    osnmaDivider = osnmaSplitter()
    DataFrameTime = galCons.getSvGST(svId)
    OSNMA = galCons.getSvOsnmaOnGST(svId, DataFrameTime)
    
    osnmaDivider.osnmaSubFrame2hkRootMack(OSNMA)
    DSM_ID = osnmaDivider.getDSMId()
    DSM_BID = osnmaDivider.getDSMBlockId()
    DSM_Block = osnmaDivider.getDSMBlock()
    DSM_NMAS = osnmaDivider.getNMAS()
    DSM_CID = osnmaDivider.getCID()
    DSM_CDPKS =osnmaDivider.getCDPKS()
    NMAHeader = osnmaDivider.getNMAHeader()
    return DSM_ID, DSM_BID, DSM_Block, DSM_NMAS, DSM_CID, DSM_CDPKS, NMAHeader

    b = bitarray()
    b.frombytes(subFrame[1])
    word4_num = b[0:6]
    word4 = b[6:126]

def concatenateBytes(iputBytelist):
    from bitarray import bitarray
    outputlist = ""
    for item in iputBytelist:
        b = bitarray()
        b.frombytes(item)
        outputlist += b.to01()
    b = bitarray(outputlist)

    return b.tobytes()

def checkRootKey(filename,message,sig):
    import hashlib
    from hashlib import sha256
    import ecdsa
    import re
    import logging
    with open(filename, 'r') as f:
        pemFile = f.read().replace('\n', '')
    pattern = '-----BEGIN PUBLIC KEY-----(.*?)-----END PUBLIC KEY-----'
    pem_sring = re.search(pattern, pemFile).group(1)
    key = ecdsa.VerifyingKey.from_pem(pem_sring, hashfunc = hashlib.sha256)
    try:
        key.verify(sig, message)
        logging.info("Digital Signature "+sig.hex()+" verified against GSC Public Key "+pem_sring)
        return True
    except: 
        logging.warn("Digital Signature "+sig.hex()+" cannot be verified against GSC Public Key "+pem_sring)
        return False




def navData(subFrame, ADKD=0): #if no value is indicated it is assumed ADKD = 12
    
    from bitarray import bitarray
    from bitarray.util import ba2int
    word = bitarray()
    b = bitarray()
    if ADKD == 0 or ADKD == 12:
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
        
    if ADKD == 4:
        b = bitarray()
        b.frombytes(subFrame[2])
        word1_num = b[0:6]
        word1 = b[6:len(b)-3]
        
        b = bitarray()
        b.frombytes(subFrame[4])
        word2_num = b[0:6]
        word2 = b[-42:]
        
        word = word1 + word2
        
        if ba2int(word2_num) == 10: # as in position number 5 we can have wether an 8 or a 10 
            return word
        else: return False
    


