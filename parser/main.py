from osnmaPython import sv_data, DSMMessage
import osnmaPython
import csv
import binascii
key_file = open('keys.txt', 'w')
import time

sv_vector = [None for i in range(36)] #Current Issue of Galileo OS ICD states that SV (satellites) are up to 36
for i in range(36):# We create a list with 36 Objects type sv_data, 
                    #in which we will store all the Data we receive from the satellite
    sv_vector[i] = sv_data(i+1)

DSM_vector = [None for i in range(16)] # DSM ID is up to 16
for i in range(16):
    DSM_vector[i] = DSMMessage(i)

live = False #Variable to decide if we are using test data or live data
record = True #if true we will save the recorded data (e.g., for future playback)
record_filename = '25-01-2022_2.csv'
testData = './test_data/25-01-2022.csv'
COMPort = 'COM12'
boudRate = 115200
m_file = open('m.txt', 'w')


if live:
    while True:
        #1st we get the uBlox data as a list of Ublox Words to get the ubloxPags
        ubloxPages = osnmaPython.getUbloxData(record,record_filename,COMPort,boudRate)
        #2nd we transform the ubloxPages to Galileo Pages (as per UBX-19014286-R06 §3.15.1.5.1)
        #And got as an output the Galileo Space Vehicle, the Word Type, the Data, and the Osnma Page (seen as Reserved 1 in OS ICD 1.3)
        #Other information such as SAR is not necessary but ubloxData2GalileoICD can also get it
        [sv_id, word_type, data_page, osnma_page] = osnmaPython.ubloxData2GalileoICD(ubloxPages)
        sv_vector[sv_id-1].subFrameSequence(word_type,data_page, osnma_page)
        print(sv_id,sv_vector[sv_id-1].getSVId())
        #print(sv_vector[sv_id-1].getSVId(),":",sv_vector[sv_id-1].getPagePosition(), int(word_type,2))
        #if sv_vector[sv_id-1].getDataFrameCompleteStatus():
        #    print("Full dataframe for GAL SV:",sv_vector[sv_id-1].getSVId())
else:
    with open(testData) as csvfile:
        parsed_data = csv.reader(csvfile, delimiter=',')
        for row in parsed_data:
            ubloxPages = []
            for word in row: #First we will create our list of words as per ublox ICD
                ubloxPages.append(word)
        #Now it is the same as "live"
            [sv_id, word_type, data_page, osnma_page] = osnmaPython.ubloxData2GalileoICD(ubloxPages)
            sv_vector[sv_id-1].subFrameSequence(word_type,data_page, osnma_page)
            if sv_vector[sv_id-1].getDataFrameCompleteStatus() & sv_vector[sv_id-1].getOsnmaDistributionStatus():
                hkroot, mack = osnmaPython.osnmasubFrame2hkroot_mack(sv_vector[sv_id-1].getOsnmaSubFrame())
                NMAS = int(hkroot[0][0:2])
                CID = int(hkroot[0][2:4])
                CDPKS = int(hkroot[0][4:7])
                if (NMAS <= 2) & (CDPKS <= 2):
                    # we will use OSNMA only if OSNMA status is Test Or Operational (embedded in NMAS)  AND we will the blocks only if status is Nominal or End of chain 
                    # Key renewal/revocation will be implemented in future code versions
                    DSMId = int(hkroot[1][0:4],2)
                    DSMBlockId = int(hkroot[1][-4:],2)
                    block = [int(i,2) for i in hkroot[2:]]
                    mack = [int(i,2) for i in mack]
                    parsed_mack = osnmaPython.parse_mack_msg(mack, None, key_file)
                    m_vec = []
                    for i in range(len(parsed_mack)):
                        PRND = bin(parsed_mack['TagsAndInfo'][i]['PRN'])[2:].zfill(8)
                        PRNA = bin(sv_vector[sv_id-1].getSVId())[2:].zfill(8).zfill(8)
                        ADKD = bin(parsed_mack['TagsAndInfo'][i]['ADKD'])[2:].zfill(8)
                        CTR = bin(i)[2:].zfill(8)
                        navdata = osnmaPython.dataSubFrame2Navdata(sv_vector[sv_id-1].getDataSubframe(),int(ADKD,2)) #already in bits
                        GST = bin(sv_vector[sv_id-1].getTime() - 30)[2:].zfill(32)
                        NMASbin = bin(NMAS)[2:].zfill(2)
                        if navdata is not None:
                            navdata = osnmaPython.dataSubFrame2Navdata(sv_vector[sv_id-1].getDataSubframe(),int(ADKD,2)).zfill(549)
                            m = osnmaPython.computeTagMessageNopad(PRND, PRNA, GST, CTR, NMASbin, navdata)
                            m_vec.append(osnmaPython.bitstring_to_bytes(m))
                            m_file .write(str(binascii.hexlify(osnmaPython.bitstring_to_bytes(m))) + "\n")
                            m_file .flush()
                        print(m_vec)
                    DSM_vector[DSMId].addBlock(DSMBlockId, block)
                    if(DSM_vector[DSMId].isComplete()) & (DSMId<=11): #DSM from 0 to 11 mean DSM-KROOT
                        DSM_vector[DSMId].parse_dsm_kroot_msg() # When DSM Is complete and DSM is type DSM-KROOT we can parse the DSM-KROOT message
