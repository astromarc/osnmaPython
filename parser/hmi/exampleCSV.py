from datetime import datetime
from time import sleep

counter = 1
counter2 = 0;

while True:
    time = datetime.utcnow()
    f = open("logname.log", "a")
    if counter % 2 ==0:
        severity = "INFO"
        text = "SV 2 received page "+str(counter2)
    else:
        severity = "ERROR"
        text= "SV 1 lose synchro"
    f.write(str(time)+","+severity+","+ text+"\n")
    f.close()
    counter+=1
    counter2+=1
    if counter2 == 10: counter2 = 0
    sleep(1)