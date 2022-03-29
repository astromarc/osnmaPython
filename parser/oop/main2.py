import dataAcquisition
import dataProcessingGalileoFrame_inputDataTransformation
import dataProcessingGalileoFrame_svNavMessage
from dataProcessingGalileoFrame_svNavMessage import svConstellation as galConstellation
from dataProcessingGalileoFrame_svNavMessage import svNavMessage
from dataProcessingGalileoFrame_svKrootOsnmaMack import svKrootOsnmaMack
from bitarray import bitarray
from bitarray.util import int2ba
import csv

pageReader = dataAcquisition.readUbloxData('./test_data/25-01-2022.csv', ',')
pageProcessor = dataProcessingGalileoFrame_inputDataTransformation.ubloxWordsList2GalileoICD()

galCons = galConstellation(36) #currently there are up to 36 Galileo Satellites

with open('./test_data/25-01-2022.csv') as csvfile:
    reader = csv.reader(csvfile)
    lista = list(reader)

osnmaProcessor = svKrootOsnmaMack()
sat = svNavMessage()
count = 0
ublox_words = []
ublox_words = pageReader.getUbloxWordsList()
while ublox_words != None:
    pageProcessor.ublox2Galileo(ublox_words)
    if pageProcessor.getSvId() == 14:
        sat.subFrameSequence(pageProcessor.getWordType(),pageProcessor.getData(),pageProcessor.getOsnma())
        if sat.getDataFrameCompleteStatus() and sat.getOsnmaDistributionStatus():
            #print(sat.getOsnmaDistributionStatus())
            print("Osnma SubFrame = ",sat.getOsnmaSubFrame())
            osnmaProcessor.osnmaSubFrame2hkRootMack(sat.getOsnmaSubFrame())
    ublox_words = pageReader.getUbloxWordsList()

