import dataAcquisition
import dataProcessingGalileoFrame_inputDataTransformation
import dataProcessingGalileoFrame_svNavMessage
from dataProcessingGalileoFrame_svNavMessage import svConstellation as galConstellation
from dataProcessingGalileoFrame_svNavMessage import svNavMessage
from dataProcessingGalileoFrame_svNavMessage import svKrootOsnmaMack
from dataProcessingGalileoFrame_svNavMessage import NavMessageAuthenticator
from dataProcessingGalileoFrame_svNavMessage import selfAuthenticator
from bitarray import bitarray
from bitarray.util import int2ba
import csv

osnmaDivider = svKrootOsnmaMack()
pageReader = dataAcquisition.readUbloxData('./test_data/25-01-2022.csv', ',')
pageProcessor = dataProcessingGalileoFrame_inputDataTransformation.ubloxWordsList2GalileoICD()

galCons = galConstellation(36) #currently there are up to 36 Galileo Satellites

with open('./test_data/25-01-2022.csv') as csvfile:
    reader = csv.reader(csvfile)
    lista = list(reader)

authenticator = NavMessageAuthenticator()
sat = svNavMessage()
count = 0
ublox_words = []
ublox_words = pageReader.getUbloxWordsList()
while ublox_words != None:
    pageProcessor.ublox2Galileo(ublox_words)
    if pageProcessor.getSvId() == 14:
        sat.subFrameSequence(pageProcessor.getWordType(),pageProcessor.getData(),pageProcessor.getOsnma())
        if sat.getDataFrameCompleteStatus() & sat.getOsnmaDistributionStatus():
            try: sat.getDataOnGST()
            except: pass
    ublox_words = pageReader.getUbloxWordsList()

