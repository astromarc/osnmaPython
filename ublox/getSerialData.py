#The aim of this code is to create a CSV file from a SFBRX messages from ublox M9, taking into account only GALILEO satellites
#The output for the csv is set to data.csv
from serial import Serial
from pyubx2 import UBXReader
import csv
  

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

fields = ['gnssId', 'svId', 'reserved0', 'freqId', 'numWords', 'chn', 'version', 'reserved1', 'dwrd_01', 'dwrd_02', 'dwrd_03'
, 'dwrd_04', 'dwrd_05', 'dwrd_06', 'dwrd_07',  'dwrd_08', 'dwrd_09'] 

while True:
   stream = Serial('COM19', 9600, timeout=1)
   ubr = UBXReader(stream)
   (raw_data, parsed_data) = ubr.read()
   if parsed_data is not None:
      ubxList = str(parsed_data).split(",")
   stream.close()
   list = []

   for x in ubxList:
      if x != "<UBX(RXM-SFRBX":
         ubxSplit = x.split('=')[1].split(")")[0]
         #print(ubxSplit)
         list.append(ubxSplit)

   with open('data.csv', 'a', newline='') as f:
    write = csv.writer(f)
    write.writerow(list)
    f.close()
   print(list)