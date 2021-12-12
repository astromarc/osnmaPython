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
        if row[1] == "27":
            hkroot_byte = (word6 & 0x00003FC0) >> 6  # Take first byte (Starting from the end)
            hkroot_byte_r = int('{:08b}'.format(hkroot_byte)[::-1], 2) # Reverse bits
            print ("SVID: " + row[1] + " HKROOT BYTE: " + hex(hkroot_byte) + " HKROOT BYTE (REVERSED): " + hex(hkroot_byte_r))
            hkroot_sequence += hex(hkroot_byte_r) + ","
print("HKROOT Stream for SVID 27: " + hkroot_sequence)