import csv

hkroot_sequence = ""

with open('../data_processed.csv') as csvfile:
    parsed_data = csv.reader(csvfile, delimiter=',')
    first = True
    for row in parsed_data:
        if first:
            first=False
            continue
        word5=int(row[12])
        word6=int(row[13])
 #       print ("SVID:" + row[1] + " word5: " + hex(word5) + " word6: " + hex(word6))
 #       print ("HEX SVID:" + row[1] + " word5: " + hex((word5 & 0x00003FFF) << 26) + " word6: " + hex((word6 & 0xFFFFFFC0) >> 6) + " Combined words: " +  hex((word5 & 0x00003FFF) << 26 | (word6 & 0xFFFFFFC0) >> 6))
 #       print ("BINARY SVID:" + row[1] + " word5: " + bin((word5 & 0x00003FFF) << 26) + " word6: " + bin((word6 & 0xFFFFFFC0) >> 6) + " Combined words: " +  bin((word5 & 0x00003FFF) << 26 | (word6 & 0xFFFFFFC0) >> 6))
        if row[1] == "27":
            print ("SVID: " + row[1] + " HKROOT BYTE: " + hex((word5 & 0x00003FFF) >> 6))
            hkroot_sequence += hex((word5 & 0x00003FFF) >> 6) + ","
print("HKROOT Stream for SVID 27: " + hkroot_sequence)