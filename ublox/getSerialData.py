#The aim of this code is to create a CSV file from a SFBRX messages from ublox M9, taking into account only GALILEO satellites
#The output for the csv is set to data.csv
from serial import Serial
from pyubx2 import UBXReader
import csv
from datetime import datetime

fields = ['gnssId', 'svId', 'reserved0', 'freqId', 'numWords', 'chn', 'version', 'reserved1', 'dwrd_01', 'dwrd_02', 'dwrd_03'
, 'dwrd_04', 'dwrd_05', 'dwrd_06', 'dwrd_07',  'dwrd_08', 'dwrd_09']

ubxList_old = []
ubxList = []
now_receiver = datetime.now()
time_receiver = now_receiver.strftime("%H:%M:%S.%f'")[:-3]

while True:
   record = False
   ubxList_new = []
   ubxList = []
   now = datetime.now()
   current_time = now.strftime("%H:%M:%S.%f'")[:-3]
   stream = Serial('COM6', 38400,timeout=0.1, bytesize=8, parity='N', stopbits=1,)
   ubr = UBXReader(stream)
   (raw_data, parsed_data) = ubr.read()
   if parsed_data is not None:
      ubxList_new = str(parsed_data).split(",")
   stream.close()
   
   if ubxList_new == ubxList_old: #We have received the same info from uBlox receiver
      record = False
   if (ubxList_new != ubxList_old) and (ubxList_new != []): #New info from uBlox Receier
      record = True
      ubxList_old = ubxList_new
      now_receiver = now
      
   deltaTime = (now - now_receiver).total_seconds()
   
   print(current_time,"Seconds since last reception:",deltaTime,"Record Status:",record,"Received:",ubxList_new)
   
   if record:
      ubxList.append(current_time)
      for x in ubxList_new:
         if x != "<UBX(RXM-SFRBX":
            ubxSplit = x.split('=')[1].split(")")[0]
            ubxList.append(ubxSplit)
      with open('24-01-2022_oldCode.csv', 'a', newline='') as f:
         write = csv.writer(f)
         write.writerow(ubxList)
         f.close()