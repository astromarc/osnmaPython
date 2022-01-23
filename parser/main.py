from osnmaPython import sv_data, DSMMessage
import osnmaPython
import csv

sv_vector = [None for i in range(36)] #Current Issue of Galileo OS ICD states that SV (satellites) are up to 36
for i in range(36):# We create a list with 36 Objects type sv_data, 
                    #in which we will store all the Data we receive from the satellite
    sv_vector[i] = sv_data(i+1)

live = False #Variable to decide if we are using test data or live data
record = True #if true we will save the recorded data (e.g., for future playback)
record_filename = 'test.csv'
testData = 'data.csv'
COMPort = 'COM19'

if live:
    while True:
        #1st we get the uBlox data as a list of Ublox Words to get the ubloxPags
        ubloxPages = osnmaPython.getUbloxData(record,record_filename,COMPort)
        #2nd we transform the ubloxPages to Galileo Pages (as per UBX-19014286-R06 §3.15.1.5.1)
        #And got as an output the Galileo Space Vehicle, the Word Type, the Data, and the Osnma Page (seen as Reserved 1 in OS ICD 1.3)
        #Other information such as SAR is not necessary but ubloxData2GalileoICD can also get it
        [sv_id, word_type, data_page, osnma_page] = osnmaPython.ubloxData2GalileoICD(ubloxPages)
        sv_vector[sv_id-1].subFrameSequence(word_type,data_page, osnma_page)
        print("SV: ",sv_vector[sv_id-1].getSVId()," num. consecutive Pages:",sv_vector[sv_id-1].getPagePosition())
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
        #When we have a complete sub.Frame we will store the necessary data to compute the Global DSM Message
            if sv_vector[sv_id-1].getDataFrameCompleteStatus():
                print(sv_vector[sv_id-1].getSVId(),":",sv_vector[sv_id-1].getOsnmaSubframe())