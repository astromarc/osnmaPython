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
    from bitarray import bitarray
    from bitarray.util import int2ba, ba2int
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
    from bitarray import bitarray
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
